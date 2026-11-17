#!/usr/bin/env python3
"""Check that the validator catches what it is supposed to catch.

Every file _resources/_test-*.md is a deliberately non-conforming resource (skipped
from the build because its name starts with '_') carrying a line

    # EXPECT: <text the validator must print for this file>

This script runs validate_resources.py with --include-tests and asserts, for each
fixture, that a WARNING line for that file contains the expected text. It also
asserts that (a) without --include-tests the fixtures are ignored and the live
resources produce no errors, and (b) no fixture causes an ERROR on a live file.

Exit code 1 on any failure. Run it in CI after validate_resources.py.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

from common import RESOURCES_DIR, ROOT

EXPECT_RE = re.compile(r"^#\s*EXPECT:\s*(.+?)\s*$", re.M)


def run_validator(*flags: str) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_resources.py"), *flags],
                          capture_output=True, text=True, cwd=ROOT)
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    fixtures = sorted(RESOURCES_DIR.glob("_test-*.md"))
    failures: list[str] = []

    # (a) Normal run ignores fixtures and is clean.
    code, out = run_validator()
    if code != 0:
        failures.append("validate_resources.py (without fixtures) reported errors:\n" + out)
    if "_test-" in out:
        failures.append("validate_resources.py mentioned a _test- fixture without --include-tests")

    # (b) Run with fixtures: each fixture's EXPECT text must appear as a WARNING for that file,
    #     and no live file may be in ERROR.
    code, out = run_validator("--include-tests")
    lines = out.splitlines()
    for ln in lines:
        if ln.startswith("ERROR"):
            failures.append("fixture run produced an ERROR (fixtures must only warn): " + ln)

    for fx in fixtures:
        text = fx.read_text(encoding="utf-8")
        m = EXPECT_RE.search(text)
        if not m:
            failures.append(f"{fx.name}: has no '# EXPECT:' line")
            continue
        expected = m.group(1)
        tag = f"{fx.name} (skipped from build)"
        hits = [ln for ln in lines if ln.startswith("WARNING") and tag in ln and expected in ln]
        if not hits:
            related = [ln for ln in lines if tag in ln]
            failures.append(f"{fx.name}: expected a warning containing {expected!r}; got:\n    " + ("\n    ".join(related) or "(nothing)"))

    for f in failures:
        print("FAIL", f)
    print(f"{len(fixtures)} fixture(s) checked: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
