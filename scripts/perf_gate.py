#!/usr/bin/env python3
"""Performance and correctness gate based on baseline report outputs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = ROOT / "logs" / "perf" / "baseline_latest.json"


def _max_elapsed_threshold(name: str) -> float:
    key = f"PERF_MAX_MS_{name.upper()}"
    raw = os.environ.get(key)
    if raw is None:
        return 0.0
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail on perf/correctness regressions.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    report_path = args.report
    if not report_path.exists():
        print(f"[perf-gate] missing report: {report_path}", file=sys.stderr)
        return 2

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    failed = []

    for cmd in payload.get("commands", []):
        name = cmd.get("name", "unknown")
        exit_code = int(cmd.get("exit_code", 1))
        tracebacks = int(cmd.get("traceback_count", 0))
        elapsed_ms = float(cmd.get("elapsed_ms", 0.0))
        max_ms = _max_elapsed_threshold(name)

        if exit_code != 0:
            failed.append(f"{name}: exit_code={exit_code}")
        if tracebacks > 0:
            failed.append(f"{name}: traceback_count={tracebacks}")
        if max_ms > 0 and elapsed_ms > max_ms:
            failed.append(f"{name}: elapsed_ms={elapsed_ms:.1f} exceeds max={max_ms:.1f}")

    if failed:
        print("[perf-gate] FAILED")
        for line in failed:
            print(f"  - {line}")
        return 1

    print("[perf-gate] PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
