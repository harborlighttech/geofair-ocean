#!/usr/bin/env python3
"""Turn a submitted "Suggest a resource" issue into a file in _resources/.

Reads the issue body (GitHub Issue Forms render each field as a "### Label" heading
followed by its value) from a file or stdin, and writes _resources/<slug>.md with
status: in-review. Prints the path written. Used by .github/workflows/issue-to-pr.yml.

Usage: python scripts/issue_to_resource.py --body issue.md [--date YYYY-MM-DD] [--slug SLUG]
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys

from common import RESOURCES_DIR, dump_front_matter, guess_url_type, load_vocabs, slugify

HEADING_RE = re.compile(r"^###\s+(.+?)\s*$", re.M)
ID_RE = re.compile(r"\[([a-z0-9-]+)\]\s*$")

# Map form labels (see build_issue_form.py) to front-matter fields.
LABELS = {
    "Title": "title", "URL": "resource_url", "Description": "description", "Resource type": "resource_type",
    "Licence": "license", "Version date": "version_date", "Lifecycle stages": "lifecycle_stages",
    "Research areas": "research_areas", "Digital object types": "object_types", "Audience": "audience", "Expertise level": "expertise_level",
    "Access cost": "access_cost", "Primary language": "language", "Authors": "authors",
    "Learning outcomes": "learning_outcomes", "Keywords": "keywords", "Testimonials": "testimonials",
    "Notes for the page": "notes",
}
EMPTY = {"", "_No response_", "None"}


def parse_body(body: str) -> dict[str, str]:
    parts = HEADING_RE.split(body)
    out = {}
    for i in range(1, len(parts) - 1, 2):
        label, value = parts[i].strip(), parts[i + 1].strip()
        out[LABELS.get(label, label)] = "" if value in EMPTY else value
    return out


def checked(value: str) -> list[str]:
    ids = []
    for line in value.splitlines():
        line = line.strip()
        if line.startswith("- [x]") or line.startswith("- [X]"):
            m = ID_RE.search(line)
            if m:
                ids.append(m.group(1))
    return ids


def term_id(value: str) -> str | None:
    m = ID_RE.search(value or "")
    return m.group(1) if m else None


def lines(value: str) -> list[str]:
    return [ln.strip() for ln in (value or "").splitlines() if ln.strip()]


def parse_people(value: str) -> list[dict]:
    people = []
    for ln in lines(value):
        cols = [c.strip() for c in ln.split("|")]
        p = {"name": cols[0]}
        if len(cols) > 1 and cols[1] in ("Person", "Organization"):
            p["type"] = cols[1]
        if len(cols) > 2 and cols[2]:
            if "orcid.org" in cols[2]:
                p["orcid"] = cols[2]
            elif "ror.org" in cols[2]:
                p["ror"] = cols[2]
        if len(cols) > 3 and cols[3]:
            p["affiliation"] = cols[3]
        people.append(p)
    return people


def parse_testimonials(value: str) -> list[dict]:
    out = []
    for ln in lines(value):
        cols = [c.strip() for c in ln.split("|")]
        if len(cols) < 2:
            continue
        prov = {"name": cols[0]}
        text = cols[-1]
        if len(cols) >= 3 and cols[1] in ("Person", "Organization"):
            prov["type"] = cols[1]
        if len(cols) >= 4 and cols[2]:
            prov["affiliation"] = cols[2]
        out.append({"provider": prov, "text": text})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--body", help="file containing the issue body (default: stdin)")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--slug")
    args = ap.parse_args()
    body = open(args.body, encoding="utf-8").read() if args.body else sys.stdin.read()
    f = parse_body(body)
    vocabs = load_vocabs()

    data: dict = {
        "title": f.get("title", "").strip(),
        "description": " ".join(f.get("description", "").split()),
        "resource_url": f.get("resource_url", "").strip(),
    }
    data["url_type"] = guess_url_type(data["resource_url"])
    if data["url_type"] != "URL":
        data["identifier"] = data["resource_url"]
    data["resource_type"] = term_id(f.get("resource_type", "")) or ""
    lic = f.get("license", "")
    data["license"] = {"id": lic.split("—")[0].strip() if lic else "LicenseRef-Unknown"}
    data["version_date"] = f.get("version_date", "").strip() or args.date
    authors = parse_people(f.get("authors", ""))
    if authors:
        data["authors"] = authors
    lang = (f.get("language", "") or "en").split(" ")[0]
    data["language"] = lang if re.match(r"^[a-z]{2,3}$", lang) else "en"
    kws = [k.strip() for k in f.get("keywords", "").split(",") if k.strip()]
    if kws:
        data["keywords"] = kws
    aud = checked(f.get("audience", ""))
    if aud:
        data["audience"] = aud
    outcomes = lines(f.get("learning_outcomes", ""))
    if outcomes:
        data["learning_outcomes"] = outcomes
    cost = term_id(f.get("access_cost", "")) or (f.get("access_cost", "") or "no").split(" ")[0]
    data["access_cost"] = cost if cost in ("no", "yes", "maybe") else "no"
    lvl = term_id(f.get("expertise_level", "")) or (f.get("expertise_level", "") or "").strip().lower()
    if lvl in {t["id"] for t in vocabs["expertise_level"]["terms"]}:
        data["expertise_level"] = lvl
    objs = checked(f.get("object_types", ""))
    if objs:
        data["object_types"] = objs
    data["lifecycle_stages"] = checked(f.get("lifecycle_stages", ""))
    data["research_areas"] = checked(f.get("research_areas", ""))
    data["status"] = "in-review"
    tms = parse_testimonials(f.get("testimonials", ""))
    if tms:
        data["testimonials"] = tms
    data["date_added"] = args.date

    slug = args.slug or slugify(data["title"])
    path = RESOURCES_DIR / f"{slug}.md"
    n = 2
    while path.exists():
        path = RESOURCES_DIR / f"{slug}-{n}.md"
        n += 1
    body_md = (f.get("notes", "") or "").strip()
    path.write_text(dump_front_matter(data, body_md + ("\n" if body_md else "")), encoding="utf-8")
    print(path.relative_to(RESOURCES_DIR.parent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
