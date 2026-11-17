"""Shared helpers for the GeoFAIR repository scripts (Python 3.9+)."""
from __future__ import annotations

import datetime as _dt
import pathlib
import re
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESOURCES_DIR = ROOT / "_resources"
VOCAB_DIR = ROOT / "_data" / "vocab"
LICENSES_FILE = ROOT / "_data" / "licenses.yml"
SCHEMA_FILE = ROOT / "schema" / "resource.schema.json"
CONFIG_FILE = ROOT / "_config.yml"

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LOCAL_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
FILENAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)


class _Loader(yaml.SafeLoader):
    """SafeLoader that keeps YAML 1.1 'no'/'yes' handling identical to Ruby's Psych
    (both treat bare yes/no as booleans), so the validator sees what Jekyll sees."""


def load_yaml(path: pathlib.Path) -> Any:
    with open(path, encoding="utf-8") as fh:
        return yaml.load(fh, Loader=_Loader)


def is_skipped(path: pathlib.Path) -> bool:
    """A resource file whose name starts with '_' is not built by Jekyll (collection
    entries starting with '_' or '.' are 'special' and ignored). The validator still
    checks such files, but reports their problems as warnings."""
    return path.name.startswith(("_", "."))


def load_config() -> dict:
    return load_yaml(CONFIG_FILE)


def load_vocabs() -> dict[str, dict]:
    """Return {data_key: vocab} where data_key is the file stem (e.g. 'lifecycle_stage')."""
    out = {}
    for p in sorted(VOCAB_DIR.glob("*.yml")):
        out[p.stem] = load_yaml(p)
    return out


def load_licenses() -> dict:
    return load_yaml(LICENSES_FILE) or {}


def split_front_matter(text: str) -> tuple[dict, str]:
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError("no YAML front matter block (--- ... ---) at top of file")
    data = yaml.load(m.group(1), Loader=_Loader) or {}
    if not isinstance(data, dict):
        raise ValueError("front matter is not a mapping")
    return data, m.group(2)


def normalise_dates(obj: Any) -> Any:
    """YAML parses unquoted dates into date objects; the schema wants ISO strings."""
    if isinstance(obj, (_dt.date, _dt.datetime)):
        return obj.strftime("%Y-%m-%d")
    if isinstance(obj, dict):
        return {k: normalise_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalise_dates(v) for v in obj]
    return obj


def slugify(text: str, max_len: int = 80) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len].rstrip("-") or "resource"


def guess_url_type(url: str) -> str:
    u = url.lower()
    if "doi.org/" in u:
        return "DOI"
    if "hdl.handle.net/" in u:
        return "Handle"
    if "/ark:" in u:
        return "ARK"
    if "purl.org/" in u:
        return "PURL"
    if u.startswith("urn:"):
        return "URN"
    return "URL"


def resource_slug(path: pathlib.Path, fm: dict) -> str:
    """The readable slug of a resource: front matter `slug`, else the filename part after
    '<local_id>_', else the slugified title. Mirrors _plugins/resource_alias.rb."""
    if fm.get("slug"):
        return str(fm["slug"])
    lid = str(fm.get("local_id", ""))
    stem = path.stem.lstrip("_.")
    if lid and stem.startswith(lid + "_") and len(stem) > len(lid) + 1:
        return stem[len(lid) + 1:]
    return re.sub(r"[^\w]+|_+", "-", str(fm.get("title", "")).lower()).strip("-")


def dump_front_matter(data: dict, body: str = "") -> str:
    fm = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100, default_flow_style=False)
    return f"---\n{fm}---\n{body}"
