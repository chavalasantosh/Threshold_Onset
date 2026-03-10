"""
THRESHOLD_ONSET — Enterprise CLI

Single entry point with subcommands and proper exit codes.
End users can run with no args: interactive menu asks what to do and for text when needed.
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from threshold_onset.config import load_config, get_config
from threshold_onset.core.logging_config import setup_logging, get_logger
from threshold_onset.exceptions import ConfigError, EXIT_SUCCESS, EXIT_FAILURE, EXIT_CONFIG_ERROR

LOG = get_logger("cli")


def _run_script(script: str, args: list = None, cwd: Path = None) -> int:
    """Run a Python script. Returns exit code."""
    cmd = [sys.executable, str(ROOT / script)]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, cwd=str(cwd or ROOT), check=False)
    return result.returncode


def _prompt_text_if_needed(value: Optional[str], what: str = "text") -> Optional[str]:
    """If value is empty and stdin is TTY, prompt for text. Else return value."""
    if value and str(value).strip():
        return value.strip()
    try:
        from integration.interactive_prompt import prompt_text, is_interactive
        if is_interactive():
            print(f"Enter your {what} (press Enter twice when done):")
            return prompt_text(prompt_line="> ", continuation="... ") or None
    except ImportError:
        pass
    return value.strip() if value else None


def cmd_run(args: argparse.Namespace) -> int:
    """Run the full pipeline with optional input text. Prompts if no input and interactive."""
    config = get_config()
    pipeline = config.get("pipeline", {})
    tokenization_methods = pipeline.get("tokenization_methods")
    tokenization = pipeline.get("tokenization_method", "word")
    num_runs = pipeline.get("num_runs", 3)

    script_args = []
    inp = getattr(args, "input", None) or getattr(args, "text", None)
    inp = _prompt_text_if_needed(inp, "text or file path")
    if inp:
        script_args.append(inp)

    if tokenization_methods:
        LOG.info("Running full pipeline: tokenization_methods=%s (%d methods), num_runs=%s",
                 tokenization_methods, len(tokenization_methods), num_runs)
    else:
        LOG.info("Running full pipeline: tokenization=%s, num_runs=%s", tokenization, num_runs)
    code = _run_script("integration/run_complete.py", script_args)
    return code


def cmd_check(args: argparse.Namespace) -> int:
    """Quick pipeline check with user-facing output. Prompts for text if missing and interactive."""
    text = _prompt_text_if_needed(getattr(args, "text", None), "text")
    if not text:
        LOG.error("No text. Run: threshold-onset check \"Your text\"  or  threshold-onset check  (then type when asked)")
        return EXIT_FAILURE
    return _run_script("integration/run_user_result.py", [text])


def cmd_suite(args: argparse.Namespace) -> int:
    """Run full 10-step evaluation suite."""
    suite_args = []
    if args.user_text:
        suite_args = ["--user", args.user_text]
    return _run_script("main.py", suite_args)


def cmd_validate(args: argparse.Namespace) -> int:
    """Run validation only."""
    return _run_script("integration/validate_pipeline.py")


def cmd_benchmark(args: argparse.Namespace) -> int:
    """Run benchmark."""
    return _run_script("integration/benchmark.py")


def cmd_config(args: argparse.Namespace) -> int:
    """Show current config (after loading)."""
    config = get_config()
    import json
    print(json.dumps(config, indent=2))
    return EXIT_SUCCESS


def cmd_health(args: argparse.Namespace) -> int:
    """Health check: config loaded, pipeline importable. Outputs JSON."""
    import json
    from threshold_onset import __version__
    status = {
        "status": "ok",
        "version": __version__,
        "config_loaded": True,
    }
    if args.verbose:
        try:
            from threshold_onset.api import process
            r = process("test", silent=True)
            status["pipeline_ok"] = r.success
        except Exception as e:
            status["pipeline_ok"] = False
            status["pipeline_error"] = str(e)
    print(json.dumps(status, indent=2))
    return EXIT_SUCCESS


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="threshold-onset",
        description="THRESHOLD_ONSET — Structural Language Pipeline",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config JSON. Overrides THRESHOLD_ONSET_CONFIG.",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Log level. Overrides config.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory. Overrides config.",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Reduce output (errors only).",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # run
    p_run = subparsers.add_parser("run", help="Run full pipeline")
    p_run.add_argument(
        "input",
        nargs="?",
        help="Input text or file path (any format: .txt, .json, .png, .mp4, etc.)",
    )
    p_run.set_defaults(func=cmd_run)

    # check
    p_check = subparsers.add_parser("check", help="Quick pipeline check")
    p_check.add_argument("text", nargs="?", help="Input text")
    p_check.set_defaults(func=cmd_check)

    # suite
    p_suite = subparsers.add_parser("suite", help="Run full 10-step evaluation suite")
    p_suite.add_argument("--user", dest="user_text", metavar="TEXT", help="Custom input for step 10")
    p_suite.set_defaults(func=cmd_suite)

    # validate
    p_validate = subparsers.add_parser("validate", help="Run validation")
    p_validate.set_defaults(func=cmd_validate)

    # benchmark
    p_benchmark = subparsers.add_parser("benchmark", help="Run benchmark")
    p_benchmark.set_defaults(func=cmd_benchmark)

    # config
    p_config = subparsers.add_parser("config", help="Show current config")
    p_config.set_defaults(func=cmd_config)

    # health
    p_health = subparsers.add_parser("health", help="Health check (JSON)")
    p_health.add_argument("-v", "--verbose", action="store_true", help="Run pipeline smoke test")
    p_health.set_defaults(func=cmd_health)

    parsed = parser.parse_args()

    # Load config first
    try:
        load_config(parsed.config)
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return EXIT_CONFIG_ERROR

    # Apply overrides
    config = get_config()
    if parsed.log_level:
        config.setdefault("pipeline", {})["log_level"] = parsed.log_level
    if parsed.output_dir:
        config.setdefault("pipeline", {})["output_dir"] = str(parsed.output_dir)

    # Setup logging
    level = config.get("pipeline", {}).get("log_level", "INFO")
    if parsed.quiet:
        level = "ERROR"
    elif parsed.log_level:
        level = parsed.log_level
    setup_logging(level=level)

    if not parsed.command:
        # No subcommand: show interactive menu if TTY so user doesn't need to know commands
        try:
            from integration.interactive_prompt import prompt_choice, is_interactive
            if is_interactive():
                print("THRESHOLD_ONSET — What do you want to do?\n")
                choice = prompt_choice(
                    "Choose:",
                    [
                        ("1", "Run pipeline (process my text)"),
                        ("2", "Quick check (see result only)"),
                        ("3", "Full evaluation suite"),
                        ("4", "Validate pipeline"),
                        ("5", "Run benchmark"),
                        ("6", "Show this help"),
                    ],
                    default="1",
                )
                if choice == "1":
                    return cmd_run(parsed)
                if choice == "2":
                    return cmd_check(parsed)
                if choice == "3":
                    return cmd_suite(parsed)
                if choice == "4":
                    return cmd_validate(parsed)
                if choice == "5":
                    return cmd_benchmark(parsed)
        except ImportError:
            pass
        parser.print_help()
        return EXIT_SUCCESS

    return parsed.func(parsed)


if __name__ == "__main__":
    sys.exit(main())
