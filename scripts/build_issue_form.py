#!/usr/bin/env python3
"""Generate .github/ISSUE_TEMPLATE/new-resource.yml (and update-resource.yml) from the
vocabulary files, so the form's dropdowns can never drift from _data/vocab/*.yml.

Usage:
  python scripts/build_issue_form.py          # write the forms
  python scripts/build_issue_form.py --check  # exit 1 if the committed forms are stale
"""
from __future__ import annotations

import argparse
import sys

import yaml

from common import ROOT, load_config, load_licenses, load_vocabs

FORM_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"


def options(vocab: dict) -> list[str]:
    # Label first so contributors read labels; the id is in brackets and parsed back out.
    return [f"{t['label']} [{t['id']}]" for t in vocab["terms"]]


def new_resource_form(vocabs: dict, licenses: dict, cfg: dict) -> dict:
    lic_opts = [f"{k} — {v['name']}" for k, v in licenses.items()]
    return {
        "name": "Suggest a resource",
        "description": f"Propose a learning resource for the {cfg.get('title', 'GeoFAIR Resource Hub')}.",
        "title": "[resource] <title of the resource>",
        "labels": ["new-resource"],
        "body": [
            {"type": "markdown", "attributes": {"value": "Thanks for suggesting a resource. Fields marked required must be filled; everything else helps people find and judge the resource. A maintainer will review and may edit before publishing."}},
            {"type": "input", "id": "title", "attributes": {"label": "Title", "description": "As it appears on the resource itself."}, "validations": {"required": True}},
            {"type": "input", "id": "resource_url", "attributes": {"label": "URL", "description": "Landing page or persistent identifier (DOI/handle preferred).", "placeholder": "https://"}, "validations": {"required": True}},
            {"type": "textarea", "id": "description", "attributes": {"label": "Description", "description": "What it covers, how long it takes, what the learner needs first. 40–2000 characters, plain text."}, "validations": {"required": True}},
            {"type": "dropdown", "id": "resource_type", "attributes": {"label": "Resource type", "options": options(vocabs["resource_type"])}, "validations": {"required": True}},
            {"type": "dropdown", "id": "license", "attributes": {"label": "Licence", "options": lic_opts}, "validations": {"required": True}},
            {"type": "input", "id": "version_date", "attributes": {"label": "Version date", "description": "Date of the current version of the resource, YYYY-MM-DD.", "placeholder": "2025-01-31"}, "validations": {"required": True}},
            {"type": "checkboxes", "id": "lifecycle_stages", "attributes": {"label": "Lifecycle stages", "description": "Tick every stage the resource teaches (at least one).", "options": [{"label": o} for o in options(vocabs["lifecycle_stage"])]}},
            {"type": "checkboxes", "id": "research_areas", "attributes": {"label": "Research areas", "description": "Tick every topic the resource is about (at least one).", "options": [{"label": o} for o in options(vocabs["research_area"])]}},
            {"type": "checkboxes", "id": "audience", "attributes": {"label": "Audience", "options": [{"label": o} for o in options(vocabs["audience"])]}},
            {"type": "dropdown", "id": "expertise_level", "attributes": {"label": "Expertise level", "options": options(vocabs["expertise_level"])}},
            {"type": "dropdown", "id": "access_cost", "attributes": {"label": "Access cost", "description": "If it may have a cost, explain in the description.", "options": options(vocabs["access_cost"])}},
            {"type": "dropdown", "id": "language", "attributes": {"label": "Primary language", "options": ["en", "es", "fr", "de", "pt", "it", "nl", "ja", "zh", "other (say which in the description)"]}},
            {"type": "textarea", "id": "authors", "attributes": {"label": "Authors", "description": "One per line: Name | Person or Organization | ORCID or ROR URL (optional) | affiliation (optional)", "placeholder": "Jane Doe | Person | https://orcid.org/0000-0000-0000-0000 | Example University"}},
            {"type": "textarea", "id": "learning_outcomes", "attributes": {"label": "Learning outcomes", "description": "One per line: what a learner can do after using it."}},
            {"type": "input", "id": "keywords", "attributes": {"label": "Keywords", "description": "Comma-separated."}},
            {"type": "textarea", "id": "testimonials", "attributes": {"label": "Testimonials", "description": "One per line: Provider name | Person or Organization | affiliation (optional) | the testimonial text"}},
            {"type": "textarea", "id": "notes", "attributes": {"label": "Notes for the page", "description": "Optional longer notes (prerequisites, how to use it). Markdown allowed."}},
        ],
    }


def update_resource_form(cfg: dict) -> dict:
    return {
        "name": "Update a resource",
        "description": "Report a change to an existing catalogue entry (new URL, new version, obsolete, correction).",
        "title": "[update] <resource title or slug>",
        "labels": ["update-resource"],
        "body": [
            {"type": "input", "id": "slug", "attributes": {"label": "Resource slug", "description": "The last part of the resource page's URL, e.g. working-with-argo-float-profiles."}, "validations": {"required": True}},
            {"type": "dropdown", "id": "change", "attributes": {"label": "What changed?", "options": ["Correction to the description or metadata", "New version or new URL", "Resource is obsolete", "Add a testimonial", "Other"]}, "validations": {"required": True}},
            {"type": "textarea", "id": "details", "attributes": {"label": "Details", "description": "Say exactly what should change. For obsolete resources, name the replacement if there is one."}, "validations": {"required": True}},
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    vocabs, licenses, cfg = load_vocabs(), load_licenses(), load_config()
    forms = {"new-resource.yml": new_resource_form(vocabs, licenses, cfg), "update-resource.yml": update_resource_form(cfg)}
    stale = []
    for name, form in forms.items():
        text = "# GENERATED by scripts/build_issue_form.py from _data/vocab/*.yml — do not edit by hand.\n" + \
               yaml.safe_dump(form, sort_keys=False, allow_unicode=True, width=120)
        path = FORM_DIR / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            FORM_DIR.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
    if args.check:
        if stale:
            print("ERROR stale issue form(s): " + ", ".join(stale) + " — run scripts/build_issue_form.py and commit")
            return 1
        print("issue forms are in sync with the vocabularies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
