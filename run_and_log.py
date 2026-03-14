#!/usr/bin/env python3
"""
Run all main executables and save output to execution_log.txt.

Usage:
    python run_and_log.py              # Full run, save to execution_log.txt
    python run_and_log.py --quick      # Quick run (check + run_complete only)
    python run_and_log.py --out FILE   # Save to custom file
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import argparse

ROOT = Path(__file__).resolve().parent
LOG_FILE = ROOT / "execution_log.txt"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from integration.runtime.cli import build_runtime_env


def run_and_log(name: str, cmd: list, log_file: Path, env: dict) -> bool:
    """Run command, append output to log. Returns True if exit 0."""
    sep = "=" * 70
    header = f"\n{sep}\n{name}\n{datetime.now().isoformat()}\n{sep}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(header)
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(result.stdout or "")
        if result.stderr:
            f.write("\n--- stderr ---\n")
            f.write(result.stderr)
        f.write(f"\n\n[Exit: {result.returncode}]\n")
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--method-workers", type=int, default=None, dest="method_workers")
    parser.add_argument("--profile", action="store_true")
    known, _rest = parser.parse_known_args(sys.argv[1:])
    runtime_env = build_runtime_env(
        workers=known.workers,
        method_workers=known.method_workers,
        profile=known.profile,
    )

    argv = sys.argv[1:]
    out = LOG_FILE
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 < len(argv):
            out = Path(argv[i + 1])
    out = Path(out).resolve()
    quick = "--quick" in argv  # Skip full 10-step suite (main, project_viewer)

    # Clear or create file
    Path(out).write_text(
        f"THRESHOLD_ONSET Execution Log\n{datetime.now().isoformat()}\n",
        encoding="utf-8",
    )

    commands = [
        ("python main.py", [sys.executable, "main.py"]),
        ("python project_viewer.py", [sys.executable, "project_viewer.py"]),
        ('python main.py --check "indian is the place fo gods and heaven."', [sys.executable, "main.py", "--check", "indian is the place fo gods and heaven."]),
        ("python integration/run_complete.py", [sys.executable, "integration/run_complete.py"]),
    ]
    if quick:
        commands = [
            ('python main.py --check "indian is the place fo gods and heaven."', [sys.executable, "main.py", "--check", "indian is the place fo gods and heaven."]),
            ("python integration/run_complete.py", [sys.executable, "integration/run_complete.py"]),
        ]
        print("Quick mode: skipping main.py and project_viewer.py (10-step suite)")

    for name, cmd in commands:
        print(f"Running: {name} ...")
        run_and_log(name, cmd, out, runtime_env)

    print(f"\nAll output saved to: {out}")


if __name__ == "__main__":
    main()
