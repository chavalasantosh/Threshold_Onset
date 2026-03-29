#!/usr/bin/env python3
"""
Fast smoke tests for a healthy clone (imports + line codec + API).

Run from repo root:
  python scripts/dev_check.py

Exits with pytest's exit code (0 = all passed).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Minimal set: stdlib-friendly, no slow/network markers by default
SMOKE_TESTS = [
    "tests/test_line_codec.py",
    "tests/test_api.py",
]


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--tb=short",
        *SMOKE_TESTS,
    ]
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
