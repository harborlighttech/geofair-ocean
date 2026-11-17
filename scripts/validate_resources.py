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
import re
import sys

import jsonschema

from common import (FILENAME_RE, LOCAL_ID_RE, RESOURCES_DIR, SCHEMA_FILE, SLUG_RE, is_skipped,
                    load_licenses, load_vocabs, normalise_dates, split_front_matter)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="resource files (default: all of _resources/)")
    ap.add_argument("--check-urls", action="store_true", help="HEAD-request each resource_url")
    ap.add_argument("--include-tests", action="store_true", help="also check the _test-*.md fixtures (see scripts/test_validation.py)")
    args = ap.parse_args()

    files = [RESOURCES_DIR.parent / f for f in args.files] if args.files else sorted(RESOURCES_DIR.glob("*.md"))
    if not args.include_tests:
        files = [f for f in files if not f.name.startswith("_test-")]
    # Live files first, so a duplicate id or title in a skipped file is reported on
    # the skipped file (as a warning), never on the live one.
    files.sort(key=lambda f: (is_skipped(f), f.name))
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    vocabs = load_vocabs()
    licenses = load_licenses()
    vocab_ids = {k: {t["id"] for t in v["terms"]} for k, v in vocabs.items()}
    field_to_vocab = {v["field"]: k for k, v in vocabs.items()}
    # local_id of every resource file (for superseded_by checks), read up front
    all_local_ids: dict[str, str] = {}
    for p in RESOURCES_DIR.glob("*.md"):
        if is_skipped(p):
            continue  # not built, so not a valid superseded_by target
        try:
            d, _ = split_front_matter(p.read_text(encoding="utf-8"))
            if isinstance(d.get("local_id"), str):
                all_local_ids.setdefault(d["local_id"], p.name)
        except Exception:  # noqa: BLE001
            pass

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
    local_ids: dict[str, str] = {}        # exact id -> file
    local_ids_ci: dict[str, str] = {}     # lower-cased id -> file
    records: list[tuple[str, dict]] = []

    skipped = 0
    for path in files:
        name = path.name
        # Files starting with '_' are excluded from the build by Jekyll; validate them so
        # they are ready to publish, but report problems as warnings, not errors.
        if is_skipped(path):
            skipped += 1
            report = warnings
            name = f"{path.name} (skipped from build)"
            stem = path.stem.lstrip("_.")
        else:
            report = errors
            stem = path.stem
        if not FILENAME_RE.match(stem):
            report.append(f"{name}: filename may only use letters, digits, dot, dash and underscore")
        try:
            data, _body = split_front_matter(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            report.append(f"{name}: {exc}")
            continue
        data = normalise_dates(data)

        # Local identifier: present, allowed characters, unique, and the file is named after it.
        lid = data.get("local_id")
        if lid is None or lid == "":
            report.append(f"{name}: local_id is missing (required; letters, digits, '.', '-', '_')")
        elif not isinstance(lid, str):
            report.append(f"{name}: local_id must be a quoted string (YAML read {lid!r} as {type(lid).__name__})")
        elif not LOCAL_ID_RE.match(lid):
            bad = sorted({c for c in lid if not re.match(r"[A-Za-z0-9._-]", c)})
            report.append(f"{name}: local_id '{lid}' contains disallowed character(s) {bad}; allowed: letters, digits, '.', '-', '_'")
        else:
            if lid in local_ids:
                report.append(f"{name}: local_id '{lid}' is already used by {local_ids[lid]}")
            elif lid.lower() in local_ids_ci:
                report.append(f"{name}: local_id '{lid}' differs only by case from '{local_ids_ci[lid.lower()]}'; ids must be unique case-insensitively (URLs and macOS filenames collide)")
            local_ids.setdefault(lid, name)
            local_ids_ci.setdefault(lid.lower(), name)
            if stem != lid:
                report.append(f"{name}: filename must be '{lid}.md' so the canonical URL is /resources/{lid}/")
        if data.get("slug") is not None and not (isinstance(data["slug"], str) and SLUG_RE.match(data["slug"])):
            report.append(f"{name}: slug must be kebab-case (a-z, 0-9, hyphens)")

        # Common YAML trap: unquoted no/yes becomes a boolean.
        if isinstance(data.get("access_cost"), bool):
            report.append(f"{name}: access_cost must be quoted (\"no\", \"yes\" or \"maybe\"); YAML read it as a boolean")

        for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.path) or "(root)"
            report.append(f"{name}: {loc}: {err.message}")

        for field, vkey in field_to_vocab.items():
            val = data.get(field)
            if val is None:
                continue
            vals = val if isinstance(val, list) else [val]
            for v in vals:
                if v not in vocab_ids[vkey]:
                    report.append(f"{name}: {field}: '{v}' is not a term in _data/vocab/{vkey}.yml")

        lic = data.get("license")
        if isinstance(lic, dict) and lic.get("id") and lic["id"] not in licenses:
            report.append(f"{name}: license.id '{lic['id']}' is not in _data/licenses.yml")

        sup = data.get("superseded_by")
        if sup and "://" not in sup and sup not in all_local_ids:
            report.append(f"{name}: superseded_by '{sup}' is not the local_id of any resource in _resources/")
        if not data.get("object_types"):
            warnings.append(f"{name}: no object_types; the build will derive one from resource_type")
        if data.get("status") == "obsolete" and not sup:
            warnings.append(f"{name}: obsolete without superseded_by")

        t = data.get("title")
        if isinstance(t, str):
            key = t.strip().lower()
            if key in titles:
                report.append(f"{name}: duplicate title (also in {titles[key]})")
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
    note = f" ({skipped} skipped from the build: filename starts with '_')" if skipped else ""
    print(f"{len(files)} resource file(s) checked{note}: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
