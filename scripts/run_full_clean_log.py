#!/usr/bin/env python3
"""
Produce ONE full clean UTF-8 log for handoff (to Cursor or Claude).
No Tee-Object, no console code page — subprocess capture only.

Uses all options from config (no settling for one):
- Tokenization: all 9 methods (pipeline + loop + SLE per method).
- Continuation: pipeline runs continuation observation for each of pipeline.continuation_texts.
- Prediction: pipeline runs generation for each of model.prediction_methods.
- Benchmark: stress_test and benchmark use benchmark.sizes and benchmark.num_runs.

Usage:
    python scripts/run_full_clean_log.py
    python scripts/run_full_clean_log.py --quick   # Skip main.py (faster; pipeline + loop + SLE + validate + tests)
    python scripts/run_full_clean_log.py --out "path/to/log.txt"

Creates:
  - output/full_clean_log_YYYYMMDD_HHmmss.txt  (timestamped)
  - output/FULL_CLEAN_LOG.txt                  (latest, overwritten)

Give FULL_CLEAN_LOG.txt (or the timestamped file) to the next assistant.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output"
CONFIG_PATH = ROOT / "config" / "default.json"

# Canonical 9 tokenization methods (config may use "space"/"char"; we pass these to env).
TOKENIZATION_METHODS_CANONICAL = [
    "whitespace", "word", "character", "grammar", "subword",
    "subword_bpe", "subword_syllable", "subword_frequency", "byte",
]


def _get_tokenization_methods():
    """Load tokenization_methods from config or return canonical 9."""
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            data = json.load(f)
        methods = data.get("pipeline", {}).get("tokenization_methods")
        if methods and len(methods) >= 1:
            # Normalize for env: space -> whitespace, char -> character
            out = []
            for m in methods:
                if m == "space":
                    out.append("whitespace")
                elif m == "char":
                    out.append("character")
                else:
                    out.append(m)
            return out
    except Exception:
        pass
    return TOKENIZATION_METHODS_CANONICAL.copy()


def run_one(cmd: list, lines: list, env: dict) -> int:
    r = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    lines.append(r.stdout or "")
    if r.stderr:
        lines.append("\n--- stderr ---\n")
        lines.append(r.stderr)
    lines.append(f"\n[Exit code: {r.returncode}]\n")
    return r.returncode


def main():
    argv = sys.argv[1:]
    out_path = None
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 < len(argv):
            out_path = Path(argv[i + 1]).resolve()
    quick = "--quick" in argv
    base_env = {**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}
    all_methods = _get_tokenization_methods()

    # Build command list: run_complete runs once (it loops over all methods via config).
    # structural_prediction_loop and santek_sle run once per tokenization method.
    commands_full = [
        ("main.py", [sys.executable, "main.py"], base_env),
        ("main.py --check", [sys.executable, "main.py", "--check", "Action before knowledge. Function stabilizes."], base_env),
        ("run_complete.py --no-tui (all methods)", [sys.executable, "integration/run_complete.py", "--no-tui", "chinni gunde lo anni asala."], base_env),
    ]
    for idx, method in enumerate(all_methods, 1):
        env_m = {**base_env, "THRESHOLD_ONSET_TOKENIZATION": method}
        commands_full.append(
            (f"structural_prediction_loop.py  method={method} ({idx}/{len(all_methods)})",
             [sys.executable, "integration/structural_prediction_loop.py", "Action before knowledge. Function stabilizes before meaning appears."],
             env_m),
        )
    for idx, method in enumerate(all_methods, 1):
        env_m = {**base_env, "THRESHOLD_ONSET_TOKENIZATION": method}
        commands_full.append(
            (f"santek_sle.py  method={method} ({idx}/{len(all_methods)})",
             [sys.executable, "santek_sle.py"],
             env_m),
        )
    commands_full.extend([
        ("validate_pipeline.py", [sys.executable, "integration/validate_pipeline.py"], base_env),
        ("pytest (model + phase4)", [sys.executable, "-m", "pytest", "tests/test_model_api.py", "tests/test_phase4_freeze.py", "-v"], base_env),
    ])
    commands_quick = commands_full[1:]  # skip main.py

    commands = commands_quick if quick else commands_full
    if quick:
        print("Quick mode: skipping main.py (pipeline + loop + SLE + validate + tests only)")
    print(f"Using {len(all_methods)} tokenization methods: {all_methods}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamped = OUT_DIR / f"full_clean_log_{ts}.txt"
    latest = OUT_DIR / "FULL_CLEAN_LOG.txt"

    lines = [
        "=" * 70 + "\n",
        "THRESHOLD_ONSET — Full clean log for handoff\n",
        f"Generated: {datetime.now().isoformat()}\n",
        ("(Quick run: main.py skipped)\n" if quick else ""),
        f"Tokenization methods: {len(all_methods)} — {all_methods}\n",
        "Continuation texts and prediction methods: from config (use all).\n",
        "Give this file to Cursor or Claude for full context.\n",
        "=" * 70 + "\n\n",
    ]

    had_failures = False
    for name, cmd, env in commands:
        lines.append("\n" + "=" * 70 + "\n")
        lines.append(f"COMMAND: {name}\n")
        lines.append("=" * 70 + "\n\n")
        code = run_one(cmd, lines, env)
        had_failures = had_failures or (code != 0)
        lines.append("")

    lines.append("\n" + "=" * 70 + "\n")
    lines.append("END OF LOG\n")
    lines.append("=" * 70 + "\n")

    content = "".join(lines)

    for f in (timestamped, latest):
        f.write_text(content, encoding="utf-8")

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"Log written to: {out_path}")

    print(f"Timestamped: {timestamped}")
    print(f"Latest:      {latest}")
    print("Give FULL_CLEAN_LOG.txt (or the timestamped file) to the next assistant.")
    return 1 if had_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
