#!/usr/bin/env python3
"""Check that the built site carries the GA4 tag exactly when it should.

Usage:
    python scripts/check_analytics.py --site _site --expect absent
    python scripts/check_analytics.py --site _site --expect present --id G-CI000000
    python scripts/check_analytics.py --site _site --from-config          # decide from _config.yml

Rules checked:
  absent  -> no page references googletagmanager.com or contains the
             geofair-analytics script; no consent banner is rendered.
  present -> every HTML page carries the geofair-analytics script with the
             expected measurement id, Google Signals and ad personalisation are
             off, and each resource page's page_location is its canonical URL
             (so alias pages report the same location as the canonical page).

Exit code 1 on any failure. Run it in CI after `jekyll build`.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TAG_RE = re.compile(r'<script id="geofair-analytics" data-measurement-id="([^"]*)"')
LOCATION_RE = re.compile(r"page_location:\s*'([^']*)'")
CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]*)"')


def html_pages(site: pathlib.Path) -> list[pathlib.Path]:
    return sorted(p for p in site.rglob("*.html") if p.is_file())


def config_id() -> str:
    import yaml  # only needed for --from-config

    cfg = yaml.safe_load((ROOT / "_config.yml").read_text(encoding="utf-8")) or {}
    return str(((cfg.get("analytics") or {}).get("google") or {}).get("measurement_id") or "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default="_site")
    ap.add_argument("--expect", choices=["absent", "present"])
    ap.add_argument("--id", default="", help="measurement id expected when --expect present")
    ap.add_argument("--from-config", action="store_true", help="expect present iff _config.yml sets a measurement id")
    args = ap.parse_args()

    if args.from_config:
        args.id = config_id()
        args.expect = "present" if args.id else "absent"
    if not args.expect:
        ap.error("give --expect or --from-config")

    site = pathlib.Path(args.site)
    pages = html_pages(site)
    if not pages:
        print(f"ERROR: no HTML pages under {site}")
        return 1

    errors: list[str] = []
    for p in pages:
        text = p.read_text(encoding="utf-8", errors="replace")
        rel = p.relative_to(site)
        m = TAG_RE.search(text)
        if args.expect == "absent":
            if m or "googletagmanager.com" in text:
                errors.append(f"{rel}: analytics tag present but none expected")
            if 'id="consent-bar"' in text:
                errors.append(f"{rel}: consent banner rendered but no analytics expected")
            continue
        # present
        if not m:
            errors.append(f"{rel}: analytics tag missing")
            continue
        if args.id and m.group(1) != args.id:
            errors.append(f"{rel}: measurement id {m.group(1)!r}, expected {args.id!r}")
        if "googletagmanager.com/gtag/js" not in text:
            errors.append(f"{rel}: gtag.js loader missing")
        if "allow_google_signals: false" not in text:
            errors.append(f"{rel}: Google Signals not disabled")
        if "allow_ad_personalization_signals: false" not in text:
            errors.append(f"{rel}: ad personalisation not disabled")
        loc, canon = LOCATION_RE.search(text), CANONICAL_RE.search(text)
        if not loc:
            errors.append(f"{rel}: page_location not set")
        elif canon and loc.group(1) != canon.group(1):
            errors.append(f"{rel}: page_location {loc.group(1)} differs from canonical {canon.group(1)}")

    for e in errors:
        print("ERROR:", e)
    print(f"check_analytics: {len(pages)} pages, expected {args.expect}"
          + (f" ({args.id})" if args.expect == "present" and args.id else "")
          + f", {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
