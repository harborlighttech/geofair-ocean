# Configurable Upvote URL — Adopter Guide

**GeoFAIR Resource Hub template**
**Date:** October 9, 2026
**Audience:** Site managers deploying the Hub for a community

---

## 1. Principle

The Hub does not implement authentication, vote storage, or trust. It implements one thing: a **configurable URL** that carries resource and voter information to wherever the site manager decides votes should go.

That decision belongs to each community. A community with no infrastructure can route votes to an email inbox. A community with an institutional research-information system can route them there. Neither requires changing the site's code — only one value in `_config.yml`.

This keeps the Hub a pure static site with no backend, no secrets, and no vendor dependency, while allowing adopters to implement endorsement at whatever level of rigour suits them.

### The two halves

| Half | What it does | Required? |
| --- | --- | --- |
| **Submit** | A URL template with placeholders, opened when a user clicks the upvote icon | Yes |
| **Counts** | A public URL returning totals per resource, read nightly by a scheduled job | Optional |

Without the counts half, the site still collects votes — the manager updates displayed totals by hand. With it, totals update automatically. Both are supported; §7 covers each.

---

## 2. Site Variables

All configuration lives in `_config.yml` under a single `upvote` key.

```yaml
upvote:
  # none | mailto | page | external
  mode: external

  # Button text and icon
  label: "Endorse this resource"
  icon: "thumbs-up"              # file in /assets/icons/
  title: "Record your endorsement of this resource"

  # --- SUBMIT (required unless mode is "none") ---
  url: >-
    https://endorse.example.org/vote
    ?resource_id={resource_id}
    &community={community}
    &return={return_url}

  target: "_blank"               # _blank | _self

  # --- COUNTS (optional) ---
  counts_url: "https://endorse.example.org/counts?community={community}"
  counts_format: "json"          # json | csv
  counts_key_column: "resource_id"   # csv only

  # --- DISPLAY ---
  threshold: 10                  # hide totals below this; 0 shows all
  badge_text: "Community Endorsed"
```

Plus one site-level value used as a placeholder:

```yaml
community_id: "geofair-ocean"
```

### Available placeholders

Substituted at build time. **All values are URI-escaped automatically** — do not escape them yourself in the template.

| Placeholder | Source | Typical use |
| --- | --- | --- |
| `{resource_id}` | resource front matter `id` | The join key. Required in every mode. |
| `{title}` | resource front matter `title` | Human-readable label for the receiving system |
| `{url}` | computed | Canonical URL of the resource page |
| `{community}` | `site.community_id` | Lets one backend serve several Hubs |
| `{lifecycle_stage}` | resource front matter | Optional context |
| `{object_type}` | resource front matter | Optional context |
| `{return_url}` | computed | Where an external app should send the user back |

`{return_url}` is inert for mailto and on-site modes. Include it anyway — it is the hook an OAuth-based external application needs, and including it from the start means switching modes later is a config change rather than a template change.

**Security constraint:** the submit URL is rendered into public HTML. It can never contain an API key, token, or secret. Any receiving system that needs a credential must hold it server-side behind the URL.

---

## 3. The Clickable Icon

One include renders the button on every resource page. It is mode-aware and needs no editing when the mode changes.

`_includes/upvote.html`

```liquid
{%- assign u = site.upvote -%}
{%- if u.mode == "none" or u.mode == nil -%}
  {%- comment -%} Upvoting disabled for this community {%- endcomment -%}
{%- else -%}

  {%- comment -%} Escape each value before substitution {%- endcomment -%}
  {%- assign v_id    = include.resource.id                    | uri_escape -%}
  {%- assign v_title = include.resource.title                 | uri_escape -%}
  {%- assign v_url   = include.resource.url  | absolute_url   | uri_escape -%}
  {%- assign v_comm  = site.community_id                      | uri_escape -%}
  {%- assign v_stage = include.resource.lifecycle_stage       | uri_escape -%}
  {%- assign v_type  = include.resource.object_type           | uri_escape -%}
  {%- assign v_ret   = include.resource.url  | absolute_url   | uri_escape -%}

  {%- assign href = u.url
        | strip_newlines
        | replace: '{resource_id}',     v_id
        | replace: '{title}',           v_title
        | replace: '{url}',             v_url
        | replace: '{community}',       v_comm
        | replace: '{lifecycle_stage}', v_stage
        | replace: '{object_type}',     v_type
        | replace: '{return_url}',      v_ret -%}

  {%- assign count = include.resource.endorsements
        | default: site.data.endorsements[include.resource.id]
        | default: 0 -%}

  <div class="upvote">
    <a class="upvote-btn"
       href="{{ href }}"
       title="{{ u.title | default: u.label }}"
       {% if u.target == "_blank" %}target="_blank" rel="noopener"{% endif %}>
      <img src="/assets/icons/{{ u.icon | default: 'thumbs-up' }}.svg"
           alt="" aria-hidden="true" width="18" height="18">
      <span>{{ u.label | default: "Endorse this resource" }}</span>
    </a>

    {%- if u.threshold > 0 and count >= u.threshold -%}
      <span class="upvote-badge">{{ u.badge_text }} ({{ count }})</span>
    {%- elsif u.threshold == 0 and count > 0 -%}
      <span class="upvote-count">{{ count }} endorsements</span>
    {%- endif -%}
  </div>

{%- endif -%}
```

**Notes on the implementation.** `strip_newlines` lets the YAML folded scalar (`>-`) hold a long URL across several lines without injecting whitespace. The icon carries `alt=""` and `aria-hidden="true"` because the adjacent text already names the action — a screen reader should hear it once, not twice. The count falls back from resource front matter to the `_data` file, so both counts strategies in §7 work without template changes.

Call it from the resource layout:

```liquid
<!-- _layouts/resource.html -->
{% include upvote.html resource=page %}
```

### Styling

`assets/css/_upvote.scss`

```scss
.upvote {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 1.5rem 0;
}

.upvote-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.925rem;

  &:hover  { background: var(--surface-hover); }
  &:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
}

.upvote-badge {
  font-size: 0.85rem;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  background: var(--accent-subtle);
  color: var(--accent-strong);
}
```

---

## 4. Mode 1 — `mailto`

The icon opens the user's email client with a pre-composed message. No infrastructure, no accounts, no third-party service.

### Configuration

```yaml
upvote:
  mode: mailto
  label: "Endorse by email"
  icon: "envelope"
  target: "_self"

  url: >-
    mailto:hub-endorsements@example.org
    ?subject=%5BEndorsement%5D%20{resource_id}
    &body=I%20endorse%20this%20resource.%0A%0A
    Resource%20ID%3A%20{resource_id}%0A
    Resource%3A%20{title}%0A
    URL%3A%20{url}%0A%0A
    My%20ORCID%20iD%20(optional)%3A%20%0A
    My%20name%3A%20%0A
    My%20institution%3A%20%0A%0A
    How%20I%20have%20used%20this%20resource%3A%0A

  threshold: 10
  badge_text: "Community Endorsed"
```

Encode the body yourself: `%0A` for a newline, `%20` for a space, `%3A` for a colon. Placeholders are escaped automatically, but the surrounding literal text is not.

### Workflow

1. User clicks the icon on a resource page.
2. Their mail client opens with recipient, subject and body filled in. Blank lines prompt for ORCID iD, name, institution and a usage note.
3. User completes the blanks and sends.
4. Email arrives in the manager's inbox with a machine-readable subject: `[Endorsement] noaa-erddap`.
5. **Manager verifies** according to whatever policy the community has adopted — checking the iD resolves, confirming the sender looks plausible, or contacting the person directly.
6. **Manager records the vote**, either by editing the resource's front matter directly (§7a) or by logging it in a spreadsheet that feeds automated counts (§7b).

### Characteristics

| | |
| --- | --- |
| Setup | Minutes — one email address |
| Cost | Nothing |
| Identity | Sender's email address; anything else is self-declared |
| Dedupe | Manual, by the manager |
| Scales to | Low tens of endorsements before tallying becomes a chore |

**Known limitations.** `mailto:` fails silently for users whose browser has no mail client configured — a significant share of webmail users. The user can edit the body before sending, so structure is not guaranteed. A plain-text address in public HTML will be harvested by spam bots, so use a role address with good filtering rather than a person's.

---

## 5. Mode 2 — `page`

An upvote page hosted on the Hub itself collects structured input, then sends it onward as email. The user stays on the site through the form, which fixes the main usability problems with raw `mailto:`.

### Configuration

```yaml
upvote:
  mode: page
  label: "Endorse this resource"
  icon: "thumbs-up"
  target: "_self"

  url: "/endorse/?resource_id={resource_id}&title={title}&return={return_url}"

  # Used by the page itself
  recipient: "hub-endorsements@example.org"
  # Optional: a form-to-email service endpoint. Leave blank to use mailto.
  form_endpoint: ""

  threshold: 10
```

### The page

`endorse/index.html`

```html
---
layout: default
title: Endorse a resource
permalink: /endorse/
---

<h1>Endorse a resource</h1>

<p id="resource-line" class="lede"></p>

<form id="endorse-form">
  <input type="hidden" name="resource_id" id="resource_id">
  <input type="hidden" name="community"   value="{{ site.community_id }}">

  <label for="orcid">Your ORCID iD</label>
  <input type="text" id="orcid" name="orcid"
         pattern="^(https?://orcid\.org/)?\d{4}-\d{4}-\d{4}-\d{3}[\dX]$"
         placeholder="0000-0000-0000-0000">
  <small>
    Self-declared. We use it to attribute your endorsement; it is reviewed
    before publication and is not verified automatically.
  </small>

  <label for="name">Your name <span aria-hidden="true">*</span></label>
  <input type="text" id="name" name="name" required>

  <label for="email">Your email <span aria-hidden="true">*</span></label>
  <input type="email" id="email" name="email" required>
  <small>Not published. Used to confirm your endorsement if needed.</small>

  <label for="institution">Institution</label>
  <input type="text" id="institution" name="institution">

  <label for="usage">How have you used this resource?</label>
  <textarea id="usage" name="usage" rows="4"></textarea>
  <small>May be published as a testimonial, with your permission.</small>

  <button type="submit">Submit endorsement</button>
</form>

<script>
(function () {
  const params   = new URLSearchParams(location.search);
  const rid      = params.get('resource_id') || '';
  const title    = params.get('title') || rid;
  const returnTo = params.get('return') || '/';
  const endpoint = {{ site.upvote.form_endpoint | default: "" | jsonify }};
  const mailTo   = {{ site.upvote.recipient     | default: "" | jsonify }};

  document.getElementById('resource_id').value = rid;
  document.getElementById('resource-line').textContent =
    title ? `You are endorsing: ${title}` : 'Select a resource from the catalogue first.';

  document.getElementById('endorse-form').addEventListener('submit', function (ev) {
    const data = Object.fromEntries(new FormData(ev.target).entries());

    if (endpoint) {
      // Form-to-email service handles delivery; let the form POST normally.
      ev.target.action = endpoint;
      ev.target.method = 'POST';
      return;   // allow default submit
    }

    // No service configured — fall back to the user's mail client.
    ev.preventDefault();
    const body = [
      `Resource ID: ${data.resource_id}`,
      `Community: ${data.community}`,
      `ORCID iD: ${data.orcid || '(not provided)'}`,
      `Name: ${data.name}`,
      `Email: ${data.email}`,
      `Institution: ${data.institution || '(not provided)'}`,
      '',
      'How I have used this resource:',
      data.usage || '(none)'
    ].join('\n');

    location.href = `mailto:${mailTo}`
      + `?subject=${encodeURIComponent('[Endorsement] ' + data.resource_id)}`
      + `&body=${encodeURIComponent(body)}`;

    setTimeout(() => { location.href = returnTo; }, 1200);
  });
})();
</script>
```

The `pattern` attribute validates ORCID iD **format** only — four groups of four, final character may be `X`. It catches typos. It does not check the iD exists or belongs to the submitter; that is the manager's review step.

### Workflow

1. User clicks the icon; the Hub's own `/endorse/` page opens with the resource prefilled.
2. User completes the form. Required fields and format validation produce consistent, parseable submissions.
3. On submit, either the configured form-to-email service delivers the message, or the user's mail client opens pre-composed as a fallback.
4. Structured email arrives in the manager's inbox.
5. **Manager verifies** per community policy.
6. **Manager records the vote** via §7a or §7b.

### Characteristics

| | |
| --- | --- |
| Setup | ~1 hour, plus a form service account if used |
| Cost | Nothing, or a free tier (typically ~50 submissions/month) |
| Identity | Email address; ORCID iD and name self-declared |
| Dedupe | Manual, or automated on email+resource in a spreadsheet |
| Scales to | Low hundreds with a spreadsheet; thousands needs mode 3 |

**Why this is better than mode 1 for most adopters.** Required fields and format validation mean every submission arrives complete and parseable, which is what makes automated counts (§7b) practical. The user also sees a page on the Hub rather than a raw mail client, which reads as a designed feature rather than a mailto link.

---

## 6. Mode 3 — `external`

The icon points at an application the community operates. That application receives the parameters and does whatever the community requires: authenticate the voter, write to a database, deduplicate, rate-limit, enforce institutional policy.

The Hub neither knows nor cares what happens behind the URL.

### Configuration

```yaml
upvote:
  mode: external
  label: "Endorse with ORCID"
  icon: "orcid"
  target: "_self"

  url: >-
    https://endorse.example.org/start
    ?resource_id={resource_id}
    &community={community}
    &title={title}
    &return={return_url}

  counts_url: "https://endorse.example.org/counts?community={community}"
  counts_format: "json"

  threshold: 10
```

### What the external application must do

**Required**

1. Accept a GET request with at minimum `resource_id`.
2. Record the endorsement by whatever method the community has chosen.
3. Redirect the user to the `return` URL when finished.

**Required if `return` is honoured**

Validate the `return` value against an allowlist of your own domains before redirecting. An unchecked redirect parameter is an open redirect, and an attacker can use your application to bounce users to a hostile site under your domain's reputation.

**Required if `counts_url` is configured**

Serve totals at a public URL, as JSON:

```json
{ "noaa-erddap": 23, "cf-conventions": 41 }
```

or CSV:

```csv
resource_id,count
noaa-erddap,23
cf-conventions,41
```

Send permissive CORS headers if the endpoint will be read from a browser. The nightly harvest job (§7b) reads it server-side, so CORS is only needed for live client-side display.

### Workflow

1. User clicks the icon.
2. Browser navigates to the external application with the parameters.
3. **Application handles identity** — OAuth with ORCID, institutional SSO, a captcha, or nothing at all. This is the community's decision and the Hub imposes no requirement.
4. **Application stores the vote** in its own database, with whatever deduplication and audit trail it implements.
5. Application redirects the user back to the resource page.
6. **Nightly job** fetches `counts_url` and commits updated totals (§7b).
7. Totals render on the next site build.

### Characteristics

| | |
| --- | --- |
| Setup | Depends entirely on the application; an ORCID OAuth service is ~12 hours to build |
| Cost | Free on serverless free tiers at this scale; verify current limits |
| Identity | Whatever the application implements, up to full OAuth |
| Dedupe | Enforced server-side by the application |
| Scales to | No practical limit |

A worked ORCID OAuth implementation — authorization code flow, token exchange, hashed dedupe keys, counts endpoint — is documented separately in the ORCID upvoting implementation guide. Several communities can share one deployment of it; votes are partitioned by the `{community}` parameter.

---

## 7. Returning Counts to the Site

### 7a. Manual — no `counts_url`

The manager edits the resource file directly:

```yaml
---
id: noaa-erddap
title: NOAA ERDDAP
endorsements: 23
endorsements_updated: 2026-10-09
---
```

Commit, and the count renders on the next build. Appropriate for modes 1 and 2 at low volume. The count travels with the resource in version control, carries full git history, and survives any change of endorsement mechanism.

### 7b. Automated — with `counts_url`

A scheduled GitHub Action fetches the counts source nightly and writes `_data/endorsements.yml`.

`.github/workflows/harvest-counts.yml`

```yaml
name: Harvest endorsement counts
on:
  schedule:
    - cron: '23 3 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  harvest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install pyyaml
      - run: python scripts/harvest_counts.py
      - name: Commit if changed
        run: |
          git config user.name  'hub-bot'
          git config user.email 'hub-bot@users.noreply.github.com'
          git add _data/endorsements.yml
          git diff --staged --quiet || git commit -m 'chore: update endorsement counts'
          git push
```

`scripts/harvest_counts.py`

```python
#!/usr/bin/env python3
"""Fetch endorsement counts from the configured source into _data/endorsements.yml."""

import csv, glob, io, json, os, sys, urllib.request
import yaml

config = yaml.safe_load(open("_config.yml"))
u = config.get("upvote", {})

url = u.get("counts_url")
if not url or u.get("mode") in (None, "none"):
    print("No counts_url configured; nothing to harvest.")
    sys.exit(0)

url = url.replace("{community}", config.get("community_id", ""))

with urllib.request.urlopen(url, timeout=30) as r:
    body = r.read().decode("utf-8")

fmt = u.get("counts_format", "json")
if fmt == "json":
    counts = {str(k): int(v) for k, v in json.loads(body).items()}
elif fmt == "csv":
    key = u.get("counts_key_column", "resource_id")
    counts = {}
    for row in csv.DictReader(io.StringIO(body)):
        rid = (row.get(key) or "").strip()
        if rid:
            try:
                counts[rid] = int(float(row.get("count", 0)))
            except ValueError:
                pass
else:
    sys.exit(f"Unknown counts_format: {fmt}")

# Only accept IDs matching real resources, so a malformed or tampered
# source cannot inject arbitrary keys into site data.
valid = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob("_resources/*.md")}
counts = {k: v for k, v in counts.items() if k in valid}

os.makedirs("_data", exist_ok=True)
with open("_data/endorsements.yml", "w") as f:
    yaml.safe_dump(counts, f, default_flow_style=False, sort_keys=True)

print(f"Wrote {len(counts)} counts.")
```

The same workflow and script serve every mode and every community. Only `_config.yml` differs.

Counts update on the nightly build, not instantly. For modes where the user returns to the site after voting, show a confirmation so the delay is not read as failure.

---

## 8. Choosing a Mode

| | `mailto` | `page` | `external` |
| --- | --- | --- | --- |
| Setup effort | Minutes | ~1 hour | Varies; ~12 hrs for ORCID OAuth |
| Running cost | None | None or free tier | Usually free at this scale |
| Infrastructure | None | None | An application to operate |
| Identity strength | Self-declared | Self-declared + verified email | Up to full OAuth |
| Deduplication | Manual | Manual or spreadsheet | Automatic |
| Manager effort per vote | High | Moderate | None |
| Practical ceiling | Tens | Hundreds | Unlimited |

**Suggested path.** Start with `page`. It costs about an hour, produces structured data that can be tallied by hand or by spreadsheet, and collects testimonial text as a byproduct. Move to `external` when volume makes manual review impractical, or when the community needs verified research identity. Because `{return_url}` is already in the URL template, that migration is a configuration change.

### A note on ORCID iDs

Modes 1 and 2 collect a **self-declared** ORCID iD. A typed identifier establishes that an identifier exists, not that the person submitting it owns it. Mode 3 with OAuth is the only option here that authenticates an iD.

ORCID's own guidance asks integrators to collect authenticated iDs via OAuth rather than manual entry wherever direct collection is possible, to protect data quality across the scholarly ecosystem. That guidance is binding on ORCID member integrations; a Hub using the free Public API is not bound by it, but the reasoning applies regardless.

Practical recommendation for communities using modes 1 or 2:

- Record how each endorsement was verified, not just the total. A `verification` field with values `self-declared`, `confirmed` (the manager contacted the person) and `authenticated` (OAuth) keeps provenance honest and means records do not need rewriting if the community later moves to mode 3.
- Do not publish a self-declared ORCID iD as though ORCID vouched for it. Display iDs only for `confirmed` or `authenticated` endorsements.
- Describe totals as endorsements rather than as verified researcher endorsements unless the verification state supports that claim.

This matters because the Hub's credibility rests on handling identifiers well. A count that overstates what it can prove undermines exactly the trust the catalogue exists to build.

---

## 9. Adding a Mode

The three modes are conventions, not code paths. Any URL that accepts parameters works without template changes:

```yaml
# GitHub issue with a prefilled template
url: >-
  https://github.com/ORG/REPO/issues/new?template=endorse.yml
  &title=Endorsement:+{title}&resource-id={resource_id}

# Prefilled Google Form
url: >-
  https://docs.google.com/forms/d/e/FORM_ID/viewform?usp=pp_url
  &entry.111111111={resource_id}&entry.222222222={title}

# Institutional system
url: "https://ris.university.edu/endorse?pid={resource_id}&src={community}"
```

Whether counts return automatically depends only on whether that system can publish totals in one of the two supported shapes.

---

## 10. Setup Checklist

- [ ] Choose a mode and record the reasoning in the governance documentation
- [ ] Set `community_id` in `_config.yml`
- [ ] Configure the `upvote` block
- [ ] For `mailto` or `page`: create a role email address with spam filtering
- [ ] For `page`: decide between a form-to-email service and the mailto fallback
- [ ] For `external`: confirm the application validates the `return` parameter against an allowlist
- [ ] Set `threshold` — leaving totals hidden until a meaningful number avoids a count of 2 reading as a negative signal on a good resource
- [ ] Decide and document the verification policy for self-declared identifiers
- [ ] If using `counts_url`: enable the harvest workflow and run it once manually
- [ ] Test end to end with a real submission before launch
- [ ] Add the endorsement review step to the Open Science Ambassador workflow documentation
