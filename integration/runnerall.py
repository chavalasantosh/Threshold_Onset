#!/usr/bin/env python3
"""Run every *.py that has __main__ and save one log. Usage: python integration/runnerall.py"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output"
TIMEOUT = 120
ENV = {**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}

SKIP = {"integration/runnerall.py", "scripts/health_server.py"}


def is_runnable(p: Path) -> bool:
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
        return "__name__" in t and ('"__main__"' in t or "'__main__'" in t)
    except Exception:
        return False


def main():
    py_files = sorted(ROOT.rglob("*.py"))
    runnable = []
    for p in py_files:
        rel = p.relative_to(ROOT)
        path_str = str(rel).replace("\\", "/")
        if path_str in SKIP:
            continue
        if is_runnable(p):
            runnable.append(path_str)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = OUT_DIR / f"all_runs_log_{ts}.txt"
    latest = OUT_DIR / "ALL_RUNS_LOG.txt"

    lines = [
        "THRESHOLD_ONSET — all *.py with __main__\n",
        f"{datetime.now().isoformat()}  |  {len(runnable)} scripts\n",
        "=" * 70 + "\n\n",
    ]

    for path_str in runnable:
        print(f"Running: {path_str}")
        lines.append(f"\n{'='*70}\nCOMMAND: {path_str}\n{'='*70}\n\n")
        try:
            r = subprocess.run(
                [sys.executable, path_str],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=ENV,
                timeout=TIMEOUT,
            )
            lines.append(r.stdout or "")
            if r.stderr:
                lines.append("\n--- stderr ---\n" + r.stderr)
            lines.append(f"\n[Exit: {r.returncode}]\n")
        except subprocess.TimeoutExpired:
            lines.append(f"\n[TIMEOUT {TIMEOUT}s]\n")
        except Exception as e:
            lines.append(f"\n[ERROR: {e}]\n")

    content = "".join(lines)
    for f in (out, latest):
        f.write_text(content, encoding="utf-8")

    print(f"\nDone. Log: {latest}  ({len(runnable)} scripts)")


if __name__ == "__main__":
    main()
