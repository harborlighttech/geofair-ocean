# Harvesting Endorsement Counts — Options by Pathway

**GeoFAIR Resource Hub template**
**Date:** October 9, 2026
**Scope:** How vote data gets from each upvote pathway back into the static site

---

## 1. Two Harvest Patterns

Every option below is one of two shapes.

**Pull** — a scheduled GitHub Action fetches from a source on a timer, writes `_data/endorsements.yml` or resource front matter, commits. The site is in control; the vote system just has to publish something readable.

**Push** — the vote system calls GitHub when something changes, via `repository_dispatch`, triggering a workflow immediately. Lower latency, but requires a personal access token held by the pushing system, which means a secret to own and rotate.

**Pull is the default recommendation** for every pathway. Counts on a curated catalogue do not need to be real-time, and pull keeps all credentials inside GitHub Actions where they are managed for you. Push is worth it only when a community wants near-instant updates and already operates the sending system.

A note on the pull mechanics that applies throughout: commits made with the default `GITHUB_TOKEN` deliberately do not trigger other workflows, to prevent recursion. If the site deploys via a GitHub Action — which it does, since the Hub needs plugins beyond the default Pages gem set — a harvest job that commits straight to `main` will update the data file and **the site will never rebuild**. Two ways around it: have the harvest job run the build and deploy itself as a later step, or have it open a pull request that a human merges (merging is an external event, so it triggers the deploy normally). The PR route is also the one that gives Open Science Ambassadors a review gate, which is worth having.

---

## 2. Options by Pathway

| Pathway | Harvest options | Infra | Latency |
| --- | --- | --- | --- |
| **1. mailto** | Manual; Apps Script → Sheet; Apps Script → issues; Action → IMAP; Email Routing → Worker | None to light | Hours to days |
| **2. On-site page** | Everything above, plus form-service webhook → dispatch; Google Form → Sheet → CSV | None to light | Minutes to a day |
| **3. External app** | Pull from a counts endpoint; app pushes via dispatch | The app itself | Minutes |

Pathway 3's harvest is trivial — the application publishes JSON or CSV and the standard nightly job reads it. Pathways 1 and 2 are where the design work is, so the rest of this document focuses there.

---

## 3. Email Harvest — Six Options

### Option A — Fully manual

The manager reads the inbox, tallies, and edits resource front matter:

```yaml
---
id: noaa-erddap
endorsements: 23
endorsements_updated: 2026-10-09
---
```

**Cost:** nothing. **Effort:** roughly a minute per endorsement including verification.
**Breaks at:** a few dozen endorsements per month.

Worth keeping as the documented default for small communities. It needs no setup, no accounts, no code, and the count lands in version control with full history. Communities that never exceed a trickle of endorsements should not be pushed toward automation they then have to maintain.

---

### Option B — Apps Script → Sheet → published CSV *(recommended)*

A Google Apps Script runs on a timer, reads matching Gmail messages, parses them into a Sheet, and the Sheet's aggregate tab is published as CSV. The existing nightly harvest job consumes that CSV unchanged.

Free, no server, no GitHub token, and the Sheet doubles as the manager's review surface — they can see every submission, add a verification column, and exclude rows they reject.

**Setup**

1. Create a Sheet with tabs `submissions` and `counts`.
2. Extensions → Apps Script, paste the script below.
3. Set a time-driven trigger (every 15 minutes is ample).
4. Publish the `counts` tab only: File → Share → Publish to web → `counts` → CSV.

```javascript
/**
 * Parses endorsement emails into the submissions sheet.
 * Subject convention: [Endorsement] <resource-id>
 */
const LABEL_DONE = 'endorsement-processed';
const VALID_IDS  = null;  // or ['noaa-erddap', 'cf-conventions', ...]

function harvestEndorsements() {
  const sheet = SpreadsheetApp.getActive().getSheetByName('submissions');
  const done  = GmailApp.getUserLabelByName(LABEL_DONE)
             || GmailApp.createLabel(LABEL_DONE);

  const threads = GmailApp.search(
    'subject:"[Endorsement]" -label:' + LABEL_DONE + ' newer_than:90d'
  );

  threads.forEach(thread => {
    thread.getMessages().forEach(msg => {
      const subject = msg.getSubject() || '';
      const match   = subject.match(/\[Endorsement\]\s*([a-z0-9][a-z0-9-]{0,63})/i);
      if (!match) return;

      const resourceId = match[1].toLowerCase();
      if (VALID_IDS && VALID_IDS.indexOf(resourceId) === -1) return;

      const body = msg.getPlainBody() || '';
      sheet.appendRow([
        new Date(),
        resourceId,
        msg.getFrom(),
        field(body, 'ORCID iD'),
        field(body, 'Name'),
        field(body, 'Institution'),
        field(body, 'How I have used this resource'),
        'pending'                       // verification status, set by the manager
      ]);
    });
    thread.addLabel(done);
  });
}

function field(body, label) {
  const re = new RegExp('^\\s*' + label + '\\s*:\\s*(.*)$', 'im');
  const m  = body.match(re);
  return m ? m[1].trim() : '';
}
```

**Counts tab** — deduplicate on sender + resource, and count only rows the manager has not rejected:

```
A1: resource_id                 B1: count
A2: =UNIQUE(FILTER(submissions!B2:B, submissions!B2:B<>""))
B2: =ARRAYFORMULA(IF(A2:A="","",
      COUNTA(UNIQUE(FILTER(submissions!C2:C,
                           submissions!B2:B = A2:A,
                           submissions!H2:H <> "rejected")))))
```

Counting unique *senders* rather than rows means a resend or a duplicate submission does not inflate the total.

**Publish the `counts` tab only.** The default publish option covers the whole document, which would expose every submitter's email address. Verify this before launch.

---

### Option C — Apps Script → GitHub issues → Action rollup

The ledger model: each endorsement email becomes a GitHub issue, a scheduled Action rolls open issues into counts, and a second step closes them as counted.

This is the design you asked about. It works, and it gives a git-native audit trail where every vote is an addressable object with a review state. The cost is noise and one more secret.

**The relay** (same Apps Script host as Option B, different body):

```javascript
const GH_REPO  = 'ORG/REPO';
const GH_TOKEN = PropertiesService.getScriptProperties().getProperty('GH_TOKEN');

function emailToIssue() {
  const done = GmailApp.getUserLabelByName('endorsement-processed')
            || GmailApp.createLabel('endorsement-processed');

  GmailApp.search('subject:"[Endorsement]" -label:endorsement-processed newer_than:90d')
    .forEach(thread => {
      thread.getMessages().forEach(msg => {
        const m = (msg.getSubject() || '')
                    .match(/\[Endorsement\]\s*([a-z0-9][a-z0-9-]{0,63})/i);
        if (!m) return;

        const resourceId = m[1].toLowerCase();
        const body = [
          '<!-- endorsement -->',
          '```yaml',
          `resource_id: ${resourceId}`,
          `from: ${msg.getFrom().replace(/[<>]/g, '')}`,
          `received: ${msg.getDate().toISOString()}`,
          `orcid: ${field(msg.getPlainBody(), 'ORCID iD') || 'null'}`,
          `verification: self-declared`,
          '```',
          '',
          '**Usage note:**',
          field(msg.getPlainBody(), 'How I have used this resource') || '_none_'
        ].join('\n');

        UrlFetchApp.fetch(`https://api.github.com/repos/${GH_REPO}/issues`, {
          method: 'post',
          headers: {
            Authorization: 'Bearer ' + GH_TOKEN,
            Accept: 'application/vnd.github+json'
          },
          payload: JSON.stringify({
            title: `Endorsement: ${resourceId}`,
            body: body,
            labels: ['endorsement', 'uncounted']
          }),
          muteHttpExceptions: true
        });
      });
      thread.addLabel(done);
    });
}
```

Store the token in Apps Script under Project Settings → Script Properties, never in the code. Use a fine-grained PAT scoped to issues on that one repository.

**The rollup Action**

```yaml
name: Roll up endorsement issues
on:
  schedule:
    - cron: '37 3 * * *'
  workflow_dispatch:

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  rollup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install pyyaml

      - name: Tally uncounted endorsements
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/rollup_endorsements.py

      - uses: peter-evans/create-pull-request@v6
        with:
          branch: bot/endorsement-rollup
          title: 'Endorsement counts — review and merge'
          body-path: rollup-summary.md
          commit-message: 'chore: roll up endorsement counts'
          labels: endorsements, bot
          add-paths: _resources/*.md
```

```python
#!/usr/bin/env python3
"""Tally issues labelled endorsement+uncounted into resource front matter."""
import glob, json, os, re, subprocess
from collections import Counter
from datetime import date
import yaml

FM = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
BLOCK = re.compile(r"```yaml\n(.*?)\n```", re.S)

def gh(args):
    return subprocess.run(["gh"] + args, capture_output=True, text=True, check=True).stdout

issues = json.loads(gh([
    "issue", "list",
    "--label", "endorsement", "--label", "uncounted",
    "--state", "open", "--limit", "1000",
    "--json", "number,body"
]))

valid = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob("_resources/*.md")}

tally, seen, counted = Counter(), set(), []
for issue in issues:
    m = BLOCK.search(issue["body"] or "")
    if not m:
        continue
    meta = yaml.safe_load(m.group(1)) or {}
    rid, sender = meta.get("resource_id"), meta.get("from")
    if rid not in valid:
        continue
    if (rid, sender) in seen:          # same person, same resource
        counted.append(issue["number"])
        continue
    seen.add((rid, sender))
    tally[rid] += 1
    counted.append(issue["number"])

# Add tallies to existing front-matter counts
changes = []
for path in sorted(glob.glob("_resources/*.md")):
    raw = open(path).read()
    m = FM.match(raw)
    if not m:
        continue
    fm, body = yaml.safe_load(m.group(1)) or {}, m.group(2)
    rid = fm.get("id") or os.path.splitext(os.path.basename(path))[0]
    if not tally.get(rid):
        continue
    old = fm.get("endorsements", 0)
    fm["endorsements"] = old + tally[rid]
    fm["endorsements_updated"] = date.today().isoformat()
    changes.append((rid, old, fm["endorsements"]))
    with open(path, "w") as f:
        f.write("---\n")
        yaml.safe_dump(fm, f, default_flow_style=False, sort_keys=False)
        f.write("---\n" + body)

# Mark the issues as counted
for number in counted:
    gh(["issue", "edit", str(number),
        "--remove-label", "uncounted", "--add-label", "counted"])
    gh(["issue", "close", str(number), "--comment", "Counted in the nightly rollup."])

lines = ["| Resource | Was | Now | Δ |", "| --- | ---: | ---: | ---: |"]
for rid, old, new in sorted(changes, key=lambda c: c[2] - c[1], reverse=True):
    flag = " ⚠️" if new - old >= 10 else ""
    lines.append(f"| `{rid}` | {old} | {new} | {new-old:+d}{flag} |")
if not changes:
    lines = ["No new endorsements."]
lines.append(f"\nIssues closed as counted: {len(counted)}")

open("rollup-summary.md", "w").write("\n".join(lines))
print("\n".join(lines))
```

**Important caveat on ordering.** The script closes issues *before* the PR is merged. If the PR is then rejected, the votes are marked counted but never applied — they are lost. Two fixes: either move the close step into a separate workflow that runs on PR merge, or have the rollup label issues `pending-merge` and close them only once the counts land on `main`. For anything beyond a pilot, use the merge-triggered close.

**When this is worth it.** Only when the community genuinely wants a per-vote audit trail in git. For counts alone, Option B does the same job with less machinery and no token.

**One more consideration.** The RFP makes the issue queue the governance workflow — resource submissions, deprecations, restorations, all reviewed by OSAs. Pouring vote issues into the same queue degrades the thing the Hub runs on. If you adopt this, put endorsements in a separate repository, or filter the OSA review board to exclude the `endorsement` label.

---

### Option D — GitHub Action polls the mailbox directly

No third-party service at all. A scheduled Action connects to the mailbox over IMAP, parses, and commits.

```yaml
name: Harvest endorsement email
on:
  schedule:
    - cron: '19 */6 * * *'
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  harvest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install pyyaml
      - env:
          IMAP_HOST: ${{ secrets.IMAP_HOST }}
          IMAP_USER: ${{ secrets.IMAP_USER }}
          IMAP_PASS: ${{ secrets.IMAP_PASS }}
        run: python scripts/harvest_imap.py
      - uses: peter-evans/create-pull-request@v6
        with:
          branch: bot/endorsement-email
          title: 'Endorsement counts from email'
          commit-message: 'chore: harvest endorsements from email'
          add-paths: _resources/*.md
```

The script uses Python's `imaplib` to search `SUBJECT "[Endorsement]"` with `UNSEEN`, parses the same structured body, and marks messages read.

**Trade-off:** everything lives in the repo, no vendor, no Apps Script. But mailbox credentials become repository secrets — on Gmail an app password, which grants full mailbox access. A compromised repo secret means a compromised inbox. Use a dedicated mailbox that holds nothing else, never the manager's personal account.

Actions minutes are free and unlimited on public repositories; private repositories get a monthly allowance.

---

### Option E — Cloudflare Email Routing → Worker

If the community's domain is on Cloudflare, Email Routing can deliver inbound mail to a Worker. The Worker parses and either writes to KV (then serves a counts endpoint) or calls GitHub.

Free, event-driven rather than polled, and no mailbox to secure. Requires the domain to be on Cloudflare and a Worker to maintain — reasonable for a community that already has both, overhead for one that does not.

---

### Option F — Commercial inbound parse

Postmark, SendGrid Inbound Parse, Mailgun Routes and similar accept mail at a subdomain and POST structured JSON to a webhook. Mature, reliable, better spam handling than anything above. Free tiers are limited and often time-boxed.

Reach for this only if the community is already paying for one of these services.

---

## 4. Harvest for Pathway 2 (On-Site Page)

The page produces structured submissions, which opens two routes the email pathway cannot use.

**Google Form instead of a custom page.** If the on-site page is replaced by a prefilled Google Form, responses land directly in a Sheet with no parsing at all. Publish the counts tab as CSV and the standard nightly job consumes it. This is the lowest-effort automated harvest of anything here — no Apps Script, no regex, no token. The cost is that the user leaves the Hub for a visibly Google-branded form.

**Form service webhook → `repository_dispatch`.** Services like Formspree can POST to an arbitrary endpoint on submission. Point it at the GitHub API:

```
POST https://api.github.com/repos/ORG/REPO/dispatches
{ "event_type": "endorsement", "client_payload": { "resource_id": "...", "email": "..." } }
```

```yaml
on:
  repository_dispatch:
    types: [endorsement]
```

Near-instant updates. Requires a PAT held by the form service, and most free tiers restrict custom webhooks — check before designing around it.

---

## 5. Spam

This matters more than anything else in the automated options, and it is easy to overlook.

An email address rendered into public HTML will be harvested within weeks. For Option A that means junk the manager deletes. For Options B through F it means **junk that automatically creates issues or rows**, and in Option C junk that automatically becomes counted votes.

Defences, in order of effectiveness:

1. **Require the subject pattern.** `[Endorsement] <resource-id>` with a strict regex. Generic spam will not match.
2. **Validate the resource ID against real resources.** The scripts above do this — an ID not matching a file in `_resources/` is dropped. This alone eliminates almost everything.
3. **Never auto-publish.** Every automated option here routes through a pull request or a manager-reviewable sheet. Nothing reaches the site without a human merge.
4. **Rate-limit per sender.** Cap submissions per address per day in the parsing step.
5. **Use a dedicated mailbox**, not the manager's. Contains the blast radius and lets you apply aggressive filtering that you would not want on a working inbox.
6. **Obfuscate the address** in the rendered page if using mailto mode — modest help, not a substitute for the above.

Requirements 1 through 3 together are sufficient for a site at this scale. Do not skip 3: an automated path straight from inbox to published count is the one configuration that can be abused silently.

---

## 6. Recommendation by Community Capacity

| Community profile | Pathway | Harvest | Setup |
| --- | --- | --- | --- |
| No technical capacity, low volume | mailto | **A — manual** | Minutes |
| No technical capacity, wants automation | page or Google Form | **B — Apps Script → Sheet → CSV** | ~2 hours |
| Wants a git-native audit trail | page | **C — email → issues → rollup** | ~6 hours |
| Avoids third-party services | page | **D — Action polls IMAP** | ~4 hours |
| Already on Cloudflare | page | **E — Email Routing → Worker** | ~4 hours |
| Operates its own application | external | **Pull from counts endpoint** | Part of the app |

**Default for the template: Option B.** It is free, requires no GitHub token, no mailbox credentials in repository secrets, and no third-party vendor beyond the Google account most communities already have. The Sheet is a genuinely useful review surface — the manager sees each submission with its self-declared ORCID iD and can mark rows verified or rejected, which is exactly the review step the trust model needs.

Option C is the more interesting design and the right answer if a community wants every vote to be an addressable, reviewable object with history. It is also roughly three times the setup, adds a token to manage, and needs the queue-pollution question answered first. Treat it as the considered upgrade rather than the starting point.

---

## 7. Common Requirements

Whichever option a community picks:

- **Counts update on a build, not on submission.** Show a confirmation when the user returns so the delay is not read as failure.
- **Validate resource IDs** against files in `_resources/` before accepting any count. All scripts here do this; any custom integration must too.
- **Deduplicate on sender + resource,** not on message. Resends are common.
- **Route through a pull request,** both for OSA review and because a `GITHUB_TOKEN` commit will not trigger the deploy workflow.
- **Record verification state** (`self-declared`, `confirmed`, `authenticated`) alongside the count, so provenance survives a later change of pathway.
- **Flag large deltas** in the PR body. A jump of ten or more should be visible without the reviewer scanning every row.
