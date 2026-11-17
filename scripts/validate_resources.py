#!/usr/bin/env python3
"""Validate every file in _resources/ before the site is built.

Checks: YAML front matter parses; conforms to schema/resource.schema.json; every
vocabulary id exists in _data/vocab/*.yml; licence id is in _data/licenses.yml;
filename is kebab-case; titles are unique; superseded_by points at a real slug;
optionally (--check-urls) that resource_url responds.

Exit code 1 on any error. Warnings never fail the build.

Usage: python scripts/validate_resources.py [--check-urls] [files...]
"""
from __future__ import annotations

import argparse
import json
import sys

import jsonschema

from common import (RESOURCES_DIR, SCHEMA_FILE, SLUG_RE, load_licenses, load_vocabs,
                    normalise_dates, split_front_matter)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="resource files (default: all of _resources/)")
    ap.add_argument("--check-urls", action="store_true", help="HEAD-request each resource_url")
    args = ap.parse_args()

    files = [RESOURCES_DIR.parent / f for f in args.files] if args.files else sorted(RESOURCES_DIR.glob("*.md"))
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    vocabs = load_vocabs()
    licenses = load_licenses()
    vocab_ids = {k: {t["id"] for t in v["terms"]} for k, v in vocabs.items()}
    field_to_vocab = {v["field"]: k for k, v in vocabs.items()}
    all_slugs = {p.stem for p in RESOURCES_DIR.glob("*.md")}

    errors: list[str] = []
    warnings: list[str] = []

    # Vocabulary self-checks: ids unique within a file; object-type emitted values unique.
    for vkey, v in vocabs.items():
        ids = [t["id"] for t in v["terms"]]
        for dup in {i for i in ids if ids.count(i) > 1}:
            errors.append(f"_data/vocab/{vkey}.yml: duplicate term id '{dup}'")
    if "object_type" in vocabs:
        seen: dict[str, str] = {}
        for t in vocabs["object_type"]["terms"]:
            val = t.get("coar") or t.get("dcmi") or t.get("datacite")
            if not val:
                errors.append(f"_data/vocab/object_type.yml: '{t['id']}' has no coar, dcmi or datacite value to emit")
            elif val in seen:
                errors.append(f"_data/vocab/object_type.yml: '{t['id']}' and '{seen[val]}' both emit {val}; additionalType values must be unique per term")
            else:
                seen[val] = t["id"]
    titles: dict[str, str] = {}
    records: list[tuple[str, dict]] = []

    for path in files:
        name = path.name
        if not SLUG_RE.match(path.stem):
            errors.append(f"{name}: filename must be kebab-case (a-z, 0-9, hyphens)")
        try:
            data, _body = split_front_matter(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")
            continue
        data = normalise_dates(data)

        # Common YAML trap: unquoted no/yes becomes a boolean.
        if isinstance(data.get("access_cost"), bool):
            errors.append(f"{name}: access_cost must be quoted (\"no\", \"yes\" or \"maybe\"); YAML read it as a boolean")

        for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.path) or "(root)"
            errors.append(f"{name}: {loc}: {err.message}")

        for field, vkey in field_to_vocab.items():
            val = data.get(field)
            if val is None:
                continue
            vals = val if isinstance(val, list) else [val]
            for v in vals:
                if v not in vocab_ids[vkey]:
                    errors.append(f"{name}: {field}: '{v}' is not a term in _data/vocab/{vkey}.yml")

        lic = data.get("license")
        if isinstance(lic, dict) and lic.get("id") and lic["id"] not in licenses:
            errors.append(f"{name}: license.id '{lic['id']}' is not in _data/licenses.yml")

        sup = data.get("superseded_by")
        if sup and "://" not in sup and sup not in all_slugs:
            errors.append(f"{name}: superseded_by '{sup}' is not a resource slug in _resources/")
        if not data.get("object_types"):
            warnings.append(f"{name}: no object_types; the build will derive one from resource_type")
        if data.get("status") == "obsolete" and not sup:
            warnings.append(f"{name}: obsolete without superseded_by")

        t = data.get("title")
        if isinstance(t, str):
            key = t.strip().lower()
            if key in titles:
                errors.append(f"{name}: duplicate title (also in {titles[key]})")
            titles[key] = name

        if data.get("url_type") == "URL" and "doi.org/" in str(data.get("resource_url", "")):
            warnings.append(f"{name}: resource_url is a DOI; url_type should be DOI")

        records.append((name, data))

    if args.check_urls:
        try:
            import requests  # noqa: WPS433
        except ImportError:
            warnings.append("requests not installed; skipping URL checks")
        else:
            for name, data in records:
                url = data.get("resource_url")
                if not url or "example.org" in url:
                    continue
                try:
                    r = requests.head(url, allow_redirects=True, timeout=15, headers={"User-Agent": "geofair-link-check/1.0"})
                    if r.status_code in (403, 405):
                        r = requests.get(url, allow_redirects=True, timeout=20, stream=True, headers={"User-Agent": "geofair-link-check/1.0"})
                    if r.status_code >= 400:
                        warnings.append(f"{name}: resource_url returned HTTP {r.status_code}")
                except requests.RequestException as exc:
                    warnings.append(f"{name}: resource_url unreachable ({exc.__class__.__name__})")

    for w in warnings:
        print(f"WARNING {w}")
    for e in errors:
        print(f"ERROR   {e}")
    print(f"{len(files)} resource file(s) checked: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
