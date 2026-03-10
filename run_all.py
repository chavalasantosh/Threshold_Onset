#!/usr/bin/env python3
"""
Run the entire project - everything we built.

Modes:
  python run_all.py              Run full suite (10 steps, default text)
  python run_all.py --user       Run entire project with your input (prompted)
  python run_all.py --user "text"  Run entire project (all 10 steps) with your text
  python run_all.py --check "text" Quick check (full pipeline, user-facing output)

Note: main.py is the primary entry point. run_all.py is equivalent.
"""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent


def run(name, script, args=None):
    """Run a script, print outcome."""
    print("\n" + "=" * 70)
    print(f"RUNNING: {name}")
    print("=" * 70)
    cmd = [sys.executable, str(ROOT / script)]
    if args:
        cmd.extend(args)
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=False,
        check=False,
    )
    ok = result.returncode == 0
    print(f"\n[{name}] {'PASS' if ok else 'FAIL'} (exit {result.returncode})")
    return ok


def main():
    # User input mode: run ENTIRE project (all 10 steps) with your text at runtime
    if len(sys.argv) >= 2 and sys.argv[1] == "--user":
        text = " ".join(sys.argv[2:]).strip() if len(sys.argv) > 2 else None
        if not text:
            print("\n" + "=" * 70)
            print("THRESHOLD_ONSET - ENTIRE PROJECT WITH YOUR INPUT")
            print("=" * 70)
            print("\nEnter your text (all 10 steps will run; step 10 uses your input):")
            try:
                text = input("> ").strip()
            except EOFError:
                text = ""
            if not text:
                print("No input.")
                return 1
        print("\nRunning entire project (10 steps) with your input...")
        results = []
        results.append(("Decoder test", run("Decoder test", "integration/test_decoder.py")))
        results.append(("Validation", run("Validation", "integration/validate_pipeline.py")))
        results.append(("Stress test", run("Stress test", "integration/stress_test.py")))
        results.append(("Benchmark", run("Benchmark", "integration/benchmark.py")))
        results.append(("Baselines", run("Baselines", "integration/baselines.py")))
        results.append(("External validation", run("External validation", "integration/external_validation.py")))
        results.append(("Stability mode", run("Stability mode", "integration/stability_mode.py")))
        results.append(("Stability experiments", run("Stability experiments", "integration/stability_experiments.py")))
        results.append(("Structural scaling", run("Structural scaling", "integration/structural_scaling.py")))
        results.append(("Full pipeline (your input)", run("Full pipeline (your input)", "integration/run_complete.py", [text])))
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        for name, ok in results:
            status = "PASS" if ok else "FAIL"
            print(f"  {name}: {status}")
        print()
        passed = sum(1 for _, ok in results if ok)
        print(f"Total: {passed}/{len(results)} passed")
        print("=" * 70)
        return 0 if passed == len(results) else 1

    # Quick check mode
    if len(sys.argv) >= 2 and sys.argv[1] == "--check":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        if not text:
            print("Usage: python run_all.py --check \"Your text here\"")
            return 1
        ok = run("Quick check", "integration/run_user_result.py", [text])
        return 0 if ok else 1

    print("\n" + "=" * 70)
    print("THRESHOLD_ONSET - FULL PROJECT RUN")
    print("=" * 70)
    print("\nTip: python main.py --user \"Your text\"  or  python run_all.py --user \"Your text\"")
    print("\nRunning everything we built:")
    print("  1. Decoder test")
    print("  2. Validation (7 input types)")
    print("  3. Stress test (scale 100-5000 tokens)")
    print("  4. Benchmark (39 samples)")
    print("  5. Baselines (4 methods)")
    print("  6. External validation (136 samples)")
    print("  7. Stability mode (perturbed runs)")
    print("  8. Stability experiments (parameter sweep)")
    print("  9. Structural scaling (topology law)")
    print(" 10. Full pipeline (text -> structure -> text)")
    print()

    results = []
    results.append(("Decoder test", run("Decoder test", "integration/test_decoder.py")))
    results.append(("Validation", run("Validation", "integration/validate_pipeline.py")))
    results.append(("Stress test", run("Stress test", "integration/stress_test.py")))
    results.append(("Benchmark", run("Benchmark", "integration/benchmark.py")))
    results.append(("Baselines", run("Baselines", "integration/baselines.py")))
    results.append(("External validation", run("External validation", "integration/external_validation.py")))
    results.append(("Stability mode", run("Stability mode", "integration/stability_mode.py")))
    results.append(("Stability experiments", run("Stability experiments", "integration/stability_experiments.py")))
    results.append(("Structural scaling", run("Structural scaling", "integration/structural_scaling.py")))
    results.append(("Full pipeline", run("Full pipeline", "integration/run_complete.py")))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {name}: {status}")
    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"Total: {passed}/{len(results)} passed")
    print("=" * 70)

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
