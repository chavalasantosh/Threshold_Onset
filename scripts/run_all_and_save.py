#!/usr/bin/env python3
"""
Run your full command list and save each command's output to a timestamped folder.
No transcript — only the actual stdout/stderr of each command.

Usage:
    python scripts/run_all_and_save.py

Output: output/runs/YYYYMMDD_HHmmss/ with 01_main.txt, 02_check.txt, ... summary.txt
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "output" / "runs"

# Your exact list: (output_filename, description, command_args)
COMMANDS = [
    ("01_main.txt", "main.py", [sys.executable, "main.py"]),
    ("02_check.txt", "main.py --check", [sys.executable, "main.py", "--check", "chinni gunde lo anni asala."]),
    ("03_run_complete_empty.txt", "run_complete.py \"\"", [sys.executable, "integration/run_complete.py", ""]),
    ("04_run_complete_notui.txt", "run_complete.py --no-tui", [sys.executable, "integration/run_complete.py", "--no-tui", "inka yenni dhachi navoo dhanni lona"]),
    ("05_model.txt", "model_predict_next", [sys.executable, "integration/model_predict_next.py", "Action before knowledge. Function stabilizes, oohaa lo illa telave ala."]),
    ("06_model_learn.txt", "model_predict_next --learn", [sys.executable, "integration/model_predict_next.py", "--learn", "oohaa lo illa telave ala."]),
    ("07_model_learn_eta.txt", "model_predict_next --learn --eta 0.1", [sys.executable, "integration/model_predict_next.py", "--learn", "--eta", "0.1", "vinthalanni chuputhanu natho raaa illa"]),
    ("08_pytest_all.txt", "pytest all", [sys.executable, "-m", "pytest", "tests/", "threshold_onset/semantic/tests/", "-v"]),
    ("09_pytest_model.txt", "pytest model_api", [sys.executable, "-m", "pytest", "tests/test_model_api.py", "-v"]),
    ("10_pytest_phase4.txt", "pytest phase4", [sys.executable, "-m", "pytest", "tests/test_phase4_freeze.py", "-v"]),
    ("11_pytest_semantic.txt", "pytest semantic", [sys.executable, "-m", "pytest", "threshold_onset/semantic/tests/", "-v"]),
    ("12_crush_all.txt", "crush --all", [sys.executable, "validation_crush/crush_protocol.py", "--all"]),
    ("13_crush_A.txt", "crush --phase A", [sys.executable, "validation_crush/crush_protocol.py", "--phase", "A"]),
    ("14_semantic_discovery.txt", "run_semantic_discovery", [sys.executable, "run_semantic_discovery.py"]),
    ("15_semantic_workflow.txt", "semantic example workflow", [sys.executable, "threshold_onset/semantic/example_complete_workflow.py"]),
    ("16_test_decoder.txt", "test_decoder", [sys.executable, "integration/test_decoder.py"]),
    ("17_validate_pipeline.txt", "validate_pipeline", [sys.executable, "integration/validate_pipeline.py"]),
]


def run_one(cmd: list, out_file: Path) -> int:
    env = {**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(r.stdout or "")
        if r.stderr:
            f.write("\n--- stderr ---\n")
            f.write(r.stderr)
        f.write(f"\n\n[Exit code: {r.returncode}]\n")
    return r.returncode


def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_DIR / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output folder: {run_dir}\n")
    results = []
    had_failures = False
    for filename, desc, cmd in COMMANDS:
        out_file = run_dir / filename
        print(f"Running: {desc} ...")
        code = run_one(cmd, out_file)
        results.append((filename, code))
        had_failures = had_failures or (code != 0)
        print(f"  -> {filename} (exit {code})")

    summary = run_dir / "summary.txt"
    with open(summary, "w", encoding="utf-8") as f:
        f.write(f"Run: {ts}\n\n")
        for fn, c in results:
            f.write(f"  {fn}  exit={c}\n")
    print(f"\nDone. All output in: {run_dir}")
    print(f"Summary: {summary}")
    return 1 if had_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
