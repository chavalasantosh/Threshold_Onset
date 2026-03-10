#!/usr/bin/env python3
"""
Run THRESHOLD_ONSET on user-provided input.

Usage:
  python integration/run_user_input.py
  python integration/run_user_input.py "Your text here"
  echo "Your text" | python integration/run_user_input.py
"""

import sys
import importlib.util
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load benchmark module directly (avoids integration package path issues)
_spec = importlib.util.spec_from_file_location(
    "benchmark", project_root / "integration" / "benchmark.py"
)
_benchmark = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_benchmark)
run_pipeline = _benchmark.run_pipeline


def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        print("THRESHOLD_ONSET - User Input Check")
        print("=" * 50)
        print("Enter text (or run with: python run_user_input.py \"Your text\")")
        print()
        try:
            text = input("Input: ").strip()
        except EOFError:
            print("No input.")
            return 1

    if not text:
        print("Empty input.")
        return 1

    print()
    print("Running pipeline...")
    ok, metrics = run_pipeline(text)

    if not ok:
        print("FAILED: Pipeline did not complete.")
        return 1

    print()
    print("=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Input:     {repr(text)}")
    print(f"Tokens:    {metrics['tokens']}")
    print(f"Output:    {metrics['decoded']}")
    print()
    print(f"Tokens:    {metrics['n_tokens']}")
    print(f"Symbols:   {metrics['n_symbols']}")
    print(f"Identities:{metrics['n_identities']}")
    print(f"Edges:     {metrics['n_edges']}")
    print()
    print(f"Self-transitions:  {metrics['constraint_violations']}")
    print(f"Self-trans. rate:  {metrics['self_transition_rate']:.1%}")
    print(f"Decoder consistency: {metrics['decoder_consistency']:.1%}")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
