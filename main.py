#!/usr/bin/env python3
"""
THRESHOLD_ONSET — Structural Language Pipeline

Entry point for the full evaluation suite. End users can run with no parameters:
  python main.py   → interactive menu: choose Quick check, Full suite with my text, or Full suite.
  python main.py --check   → prompts for your text (no need to quote on command line)
  python main.py --user    → prompts for your text, then runs full suite
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from integration.runtime.cli import build_runtime_env
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

PIPELINE_STEPS: List[Tuple[str, str]] = [
    ("Decoder test", "integration/test_decoder.py"),
    ("Validation", "integration/validate_pipeline.py"),
    ("Stress test", "integration/stress_test.py"),
    ("Benchmark", "integration/benchmark.py"),
    ("Baselines", "integration/baselines.py"),
    ("External validation", "integration/external_validation.py"),
    ("Stability mode", "integration/stability_mode.py"),
    ("Stability experiments", "integration/stability_experiments.py"),
    ("Structural scaling", "integration/structural_scaling.py"),
    ("Full pipeline", "integration/run_complete.py"),
]


def _run_step(
    name: str,
    script: str,
    args: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
) -> bool:
    """Execute a pipeline step. Returns True if exit code is 0."""
    sep = "=" * 70
    print(f"\n{sep}\nRUNNING: {name}\n{sep}")
    cmd = [sys.executable, str(ROOT / script)]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=False, check=False)
    status = "PASS" if result.returncode == 0 else "FAIL"
    print(f"\n[{name}] {status} (exit {result.returncode})")
    return result.returncode == 0


def _print_header(title: str) -> None:
    separator = "=" * 70
    print(f"\n{separator}\n{title}\n{separator}")


def _print_summary(results: List[Tuple[str, bool]]) -> None:
    _print_header("SUMMARY")
    for name, passed in results:
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
    passed_count = sum(1 for _, p in results if p)
    total = len(results)
    print(f"\nTotal: {passed_count}/{total} passed")
    print("=" * 70)


def _run_full_suite(user_text: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> int:
    """Execute all pipeline steps. If user_text is provided, step 10 uses it."""
    results: List[Tuple[str, bool]] = []
    for i, (name, script) in enumerate(PIPELINE_STEPS):
        step_name = f"{name} (your input)" if user_text and i == len(PIPELINE_STEPS) - 1 else name
        args = [user_text] if user_text and i == len(PIPELINE_STEPS) - 1 else None
        passed = _run_step(step_name, script, args, env=env)
        results.append((step_name, passed))
    _print_summary(results)
    return EXIT_SUCCESS if all(p for _, p in results) else EXIT_FAILURE


def _prompt_user_input() -> Optional[str]:
    """Read user input from stdin (multi-line). Returns None if empty or EOF."""
    try:
        from integration.interactive_prompt import prompt_text, is_interactive
        if is_interactive():
            return prompt_text(
                "Enter your text (step 10 / pipeline will use it):",
                prompt_line="> ",
                continuation="... ",
            ) or None
        return input("> ").strip() or None
    except ImportError:
        try:
            return input("> ").strip() or None
        except EOFError:
            return None
    except EOFError:
        return None


def _parse_args() -> Tuple[str, Optional[str], argparse.Namespace]:
    """Parse argv into (mode, text). Modes: 'full' | 'user' | 'check'."""
    argv = sys.argv
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--method-workers", type=int, default=None, dest="method_workers")
    parser.add_argument("--profile", action="store_true")
    known, _rest = parser.parse_known_args(argv[1:])
    filtered: List[str] = []
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg in ("--workers", "--method-workers"):
            i += 2
            continue
        if arg == "--profile":
            i += 1
            continue
        filtered.append(arg)
        i += 1

    if not filtered:
        return "full", None, known
    mode = filtered[0].lower()
    text = " ".join(filtered[1:]).strip() if len(filtered) > 1 else None
    return mode, text, known


def _interactive_menu() -> Optional[str]:
    """Show menu when user runs python main.py with no args. Returns choice: '1'|'2'|'3' or None."""
    try:
        from integration.interactive_prompt import prompt_choice, is_interactive
        if not is_interactive():
            return None
        _print_header("THRESHOLD_ONSET")
        choice = prompt_choice(
            "What do you want to do?",
            [
                ("1", "Quick check — process my text (see result only)"),
                ("2", "Full suite with my text (all 10 steps)"),
                ("3", "Full suite (default corpus, no input)"),
            ],
            default="1",
        )
        return choice
    except ImportError:
        return None


def main() -> int:
    mode, text, runtime_flags = _parse_args()
    runtime_env = build_runtime_env(
        workers=runtime_flags.workers,
        method_workers=runtime_flags.method_workers,
        profile=runtime_flags.profile,
    )

    if mode == "--check":
        if not text:
            from integration.interactive_prompt import prompt_text, is_interactive
            if is_interactive():
                _print_header("THRESHOLD_ONSET — Quick check")
                text = _prompt_user_input()
            if not text:
                print("No text provided. Run: python main.py --check \"Your text\"")
                print("  Or run: python main.py --check   and type your text when asked.")
                return EXIT_FAILURE
        passed = _run_step("Quick check", "integration/run_user_result.py", [text], env=runtime_env)
        return EXIT_SUCCESS if passed else EXIT_FAILURE

    if mode == "--user":
        if not text:
            _print_header("THRESHOLD_ONSET — Full suite with your text")
            text = _prompt_user_input()
        if not text:
            print("No input provided.")
            return EXIT_FAILURE
        print("\nRunning full suite with your input...")
        print("-" * 40)
        for line in text.strip().split("\n"):
            print(f"  {line}")
        print("-" * 40)
        return _run_full_suite(user_text=text, env=runtime_env)

    # No args: interactive menu (or full suite if not TTY)
    if len(sys.argv) < 2:
        choice = _interactive_menu()
        if choice == "1":
            _print_header("THRESHOLD_ONSET — Quick check")
            text = _prompt_user_input()
            if not text:
                print("No text entered.")
                return EXIT_FAILURE
            passed = _run_step("Quick check", "integration/run_user_result.py", [text], env=runtime_env)
            return EXIT_SUCCESS if passed else EXIT_FAILURE
        if choice == "2":
            text = _prompt_user_input()
            if not text:
                print("No text entered.")
                return EXIT_FAILURE
            print("\nRunning full suite with your text...")
            return _run_full_suite(user_text=text, env=runtime_env)
        if choice == "3":
            _print_header("THRESHOLD_ONSET — Full Evaluation Suite")
            return _run_full_suite(env=runtime_env)
        # No choice or invalid — run full suite as before
        _print_header("THRESHOLD_ONSET — Full Evaluation Suite")
        return _run_full_suite(env=runtime_env)

    # Default: full suite with default corpus
    _print_header("THRESHOLD_ONSET — Full Evaluation Suite")
    return _run_full_suite(env=runtime_env)


if __name__ == "__main__":
    sys.exit(main())
