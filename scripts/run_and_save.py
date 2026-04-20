#!/usr/bin/env python3
"""
Run essentials (or full suite) and save all output to a timestamped folder for analysis.

Usage:
    python scripts/run_and_save.py
    python scripts/run_and_save.py --full
    python scripts/run_and_save.py --out my_runs

Output:
    output/runs/YYYYMMDD_HHmmss/
        01_check.txt          pipeline quick check
        02_model_no_learn.txt  predict-next accuracy (no learning)
        03_model_learn.txt    predict-next accuracy (with learning)
        04_model_tests.txt     pytest model API
        [05_suite.txt]        full 10-step suite (only if --full)
        summary.txt           list of files and exit codes
"""

import contextlib
import io
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_OUT_DIR = ROOT / "output" / "runs"
SAMPLE_TEXT = "Action before knowledge. Function stabilizes before meaning appears."


def run_check_direct(out_file: Path) -> int:
    """Run pipeline in-process; capture full output to out_file. No main.py, no run_user_result."""
    out_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        from integration.run_complete import run, PipelineConfig
        cfg = PipelineConfig.from_project()
        cfg.show_tui = False
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            result = run(text_override=SAMPLE_TEXT, cfg=cfg, return_result=True, return_model_state=False)
        out = buf.getvalue()
        if result is None:
            out_file.write_text(out + "\n[Exit code: 1]\n", encoding="utf-8")
            return 1
        out_file.write_text(out + f"\n[Exit code: 0]\n", encoding="utf-8")
        return 0
    except Exception as e:
        out_file.write_text(f"Error: {e}\n[Exit code: 1]\n", encoding="utf-8")
        return 1


def run_step(name: str, cmd: list, out_file: Path) -> int:
    """Run command, write stdout+stderr to out_file. Return exit code."""
    out_file.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
    )
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(result.stdout or "")
        if result.stderr:
            f.write("\n--- stderr ---\n")
            f.write(result.stderr)
        f.write(f"\n\n[Exit code: {result.returncode}]\n")
    return result.returncode


def main() -> int:
    argv = list(sys.argv[1:])
    full_suite = "--full" in argv
    if "--full" in argv:
        argv.remove("--full")
    out_dir = DEFAULT_OUT_DIR
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 < len(argv):
            out_dir = Path(argv[i + 1]).resolve()
            if not out_dir.is_absolute():
                out_dir = (ROOT / out_dir).resolve()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = out_dir / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    steps = [
        ("01_check.txt", "Quick pipeline check", None),  # run in-process
        ("02_model_no_learn.txt", "Model (no learning)", [sys.executable, "integration/model_predict_next.py", SAMPLE_TEXT]),
        ("03_model_learn.txt", "Model (with learning)", [sys.executable, "integration/model_predict_next.py", "--learn", SAMPLE_TEXT]),
        ("04_model_tests.txt", "Model API tests", [sys.executable, "-m", "pytest", "tests/test_model_api.py", "-v"]),
    ]
    if full_suite:
        steps.append(("05_suite.txt", "Full 10-step suite", [sys.executable, "main.py"]))

    results = []
    had_failures = False
    for filename, name, cmd in steps:
        out_file = run_dir / filename
        print(f"Running: {name} ...")
        if cmd is None:
            code = run_check_direct(out_file)
        else:
            code = run_step(name, cmd, out_file)
        results.append((filename, code))
        had_failures = had_failures or (code != 0)
        print(f"  -> {out_file} (exit {code})")

    summary_path = run_dir / "summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"Run: {ts}\n")
        f.write(f"Output dir: {run_dir}\n\n")
        for filename, code in results:
            f.write(f"  {filename}  exit={code}\n")
    print(f"\nAll output saved to: {run_dir}")
    print(f"Summary: {summary_path}")
    return 1 if had_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
