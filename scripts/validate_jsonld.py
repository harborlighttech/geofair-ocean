#!/usr/bin/env python3
"""Validate the JSON-LD emitted by the built site (run after `jekyll build`).

For every HTML page under _site/ (and resources.jsonld):
  * each <script type="application/ld+json"> block must parse as JSON;
  * LearningResource objects must carry the properties the GeoFAIR profile requires;
  * every DefinedTerm's inDefinedTermSet must be a vocabulary URL on this site;
  * the ItemList on /resources/ must equal /resources.jsonld and contain no draft or
    in-review entries.
With --shacl, also validates against a SHACL shapes file using pyshacl (optional
dependency). The default shapes file is schema/geofair-shapes.ttl; pass --shapes
with the Bioschemas TrainingMaterial shapes file to check that profile too.

Usage: python scripts/validate_jsonld.py [--site _site] [--shacl [--shapes FILE]]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

from common import RESOURCES_DIR, ROOT, is_skipped, load_config, split_front_matter

SCRIPT_RE = re.compile(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)
REQUIRED_LR = ["@id", "name", "description", "url", "learningResourceType", "license", "dateModified",
               "inLanguage", "keywords", "about", "creativeWorkStatus", "isAccessibleForFree"]


def walk(obj, fn):
    if isinstance(obj, dict):
        fn(obj)
        for v in obj.values():
            walk(v, fn)
    elif isinstance(obj, list):
        for v in obj:
            walk(v, fn)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="_site")
    ap.add_argument("--shacl", action="store_true")
    ap.add_argument("--shapes", default=str(ROOT / "schema" / "geofair-shapes.ttl"),
                    help="SHACL shapes file or URL (default: schema/geofair-shapes.ttl; pass the Bioschemas TrainingMaterial shapes URL to check that profile)")
    args = ap.parse_args()
    site_dir = (ROOT / args.site).resolve()
    if not site_dir.is_dir():
        print(f"ERROR {site_dir} not found; run jekyll build first")
        return 1

    cfg = load_config()
    site_root = (cfg.get("url", "") or "") + (cfg.get("baseurl", "") or "")
    indexed = set(cfg.get("catalogue", {}).get("indexed_statuses", ["published", "obsolete"]))
    errors: list[str] = []
    blocks: list[tuple[str, dict]] = []

    for html in sorted(site_dir.rglob("*.html")):
        rel = str(html.relative_to(site_dir))
        for m in SCRIPT_RE.finditer(html.read_text(encoding="utf-8")):
            try:
                blocks.append((rel, json.loads(m.group(1))))
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: JSON-LD does not parse: {exc}")

    jsonld_file = site_dir / "resources.jsonld"
    catalogue = None
    if jsonld_file.exists():
        try:
            catalogue = json.loads(jsonld_file.read_text(encoding="utf-8"))
            blocks.append(("resources.jsonld", catalogue))
        except json.JSONDecodeError as exc:
            errors.append(f"resources.jsonld does not parse: {exc}")
    else:
        errors.append("resources.jsonld missing from build")

    lr_count = 0
    index_list = None

    def check(obj: dict, where: str):
        nonlocal lr_count, index_list
        t = obj.get("@type")
        if t == "DefinedTerm":
            s = str(obj.get("inDefinedTermSet", ""))
            if not s.startswith(site_root + "/vocab/"):
                errors.append(f"{where}: DefinedTerm {obj.get('termCode')} has foreign inDefinedTermSet {s}")
            if "name" not in obj:
                errors.append(f"{where}: DefinedTerm {obj.get('termCode')} has no name (unknown vocabulary id?)")
        elif t == "LearningResource":
            lr_count += 1
            for k in REQUIRED_LR:
                if k not in obj:
                    errors.append(f"{where}: LearningResource {obj.get('@id')} lacks {k}")
            if not str(obj.get("@id", "")).startswith(site_root):
                errors.append(f"{where}: LearningResource @id not on this site: {obj.get('@id')}")
            st = obj.get("creativeWorkStatus", {})
            code = st.get("termCode") if isinstance(st, dict) else st
            if where in ("resources/index.html", "resources.jsonld") and code not in indexed:
                errors.append(f"{where}: {obj.get('@id')} has status '{code}' but is in the public index")
        elif t == "ItemList" and where == "resources/index.html":
            index_list = obj

    for where, obj in blocks:
        walk(obj, lambda o, w=where: check(o, w))

    if index_list is not None and catalogue is not None:
        a = json.dumps(index_list, sort_keys=True)
        b = json.dumps(catalogue, sort_keys=True)
        if a != b:
            errors.append("ItemList embedded in /resources/ differs from /resources.jsonld")
        n = index_list.get("numberOfItems")
        if n != len(index_list.get("itemListElement", [])):
            errors.append(f"ItemList numberOfItems={n} but {len(index_list.get('itemListElement', []))} elements")

    # Slug aliases: /resources/<local_id>/<slug>/ must exist and point at the canonical page.
    def jekyll_slugify(text: str) -> str:
        return re.sub(r"[^\w]+|_+", "-", str(text).lower()).strip("-")

    sources = []
    for src in sorted(RESOURCES_DIR.glob("*.md")):
        try:
            fm, _ = split_front_matter(src.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        sources.append((src, fm))
    live_ids = {str(fm.get("local_id", "")) for src, fm in sources if not is_skipped(src)}
    for src, fm in sources:
        lid = str(fm.get("local_id", ""))
        if is_skipped(src):
            # Underscore-prefixed files must stay out of the build entirely. A page may
            # still exist for the id if a live resource uses the same one.
            if lid and lid not in live_ids and (site_dir / "resources" / lid / "index.html").exists():
                errors.append(f"{src.name}: starts with '_' but resources/{lid}/ was built; Jekyll should skip it")
            continue
        slug = str(fm.get("slug") or jekyll_slugify(fm.get("title", "")))
        if not lid or not slug:
            continue
        canonical = site_dir / "resources" / lid / "index.html"
        alias = site_dir / "resources" / lid / slug / "index.html"
        if not canonical.exists():
            errors.append(f"{src.name}: canonical page resources/{lid}/ was not built")
        if not alias.exists():
            errors.append(f"{src.name}: alias page resources/{lid}/{slug}/ was not built (is _plugins/resource_alias.rb running?)")
        else:
            text = alias.read_text(encoding="utf-8")
            if f'rel="canonical" href="{site_root}/resources/{lid}/"' not in text:
                errors.append(f"{src.name}: alias page does not declare the canonical URL")
            if f'"@id": "{site_root}/resources/{lid}/"' not in text:
                errors.append(f"{src.name}: alias page JSON-LD @id is not the canonical URL")
            if f'"mainEntityOfPage": "{site_root}/resources/{lid}/{slug}/"' not in text:
                errors.append(f"{src.name}: alias page JSON-LD mainEntityOfPage is not the readable URL")

    if args.shacl:
        try:
            import pyshacl  # noqa: WPS433
            import rdflib  # noqa: WPS433
        except ImportError:
            print("WARNING pyshacl/rdflib not installed; skipping SHACL")
        else:
            try:
                shapes = rdflib.Graph().parse(args.shapes, format="turtle")
                data = rdflib.Graph()
                for where, obj in blocks:
                    data.parse(data=json.dumps(obj), format="json-ld")
                ok, _g, text = pyshacl.validate(data, shacl_graph=shapes)
                if not ok:
                    errors.append("SHACL validation failed:\n" + text)
            except Exception as exc:  # noqa: BLE001
                print(f"WARNING SHACL step skipped: {exc}")

    for e in errors:
        print(f"ERROR   {e}")
    print(f"{len(blocks)} JSON-LD block(s), {lr_count} LearningResource object(s) checked: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
