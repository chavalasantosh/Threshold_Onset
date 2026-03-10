#!/usr/bin/env python3
"""
Interactive prompts for end users — no parameters required.

Use this in every script so non-technical users can run e.g.:
  python main.py
  python integration/run_complete.py
and be asked what to do instead of reading "Usage: ..." and flags.
"""

import sys
from typing import List, Optional, Tuple


def is_interactive() -> bool:
    """True if stdin looks like a terminal (user can type)."""
    try:
        return sys.stdin.isatty()
    except Exception:
        return False


def prompt_text(
    message: str = "Enter your text (press Enter twice when done):",
    prompt_line: str = "> ",
    continuation: str = "... ",
) -> str:
    """
    Ask the user to type or paste text. Multi-line: press Enter twice to finish.
    Returns empty string if nothing entered or EOF.
    """
    print(message)
    if continuation:
        print("  (Type or paste, then press Enter twice to finish.)")
    lines: List[str] = []
    try:
        while True:
            p = continuation if lines else prompt_line
            line = input(p)
            if line == "" and lines:
                break
            if line != "":
                lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines).strip() if lines else ""


def prompt_choice(
    message: str,
    choices: List[Tuple[str, str]],
    default: Optional[str] = None,
) -> Optional[str]:
    """
    Show a numbered menu and return the chosen key (e.g. "1", "2").
    choices = [("1", "Quick check"), ("2", "Full pipeline"), ...]
    Returns None on EOF or invalid.
    """
    print(message)
    for key, label in choices:
        print(f"  [{key}]  {label}")
    prompt = "Choice: "
    if default:
        prompt = f"Choice [{default}]: "
    try:
        raw = input(prompt).strip()
        if not raw and default:
            return default
        keys = [c[0] for c in choices]
        if raw in keys:
            return raw
        return None
    except EOFError:
        return default


def prompt_yes_no(message: str, default: bool = True) -> bool:
    """Ask Y/n or y/N. Returns True for yes, False for no."""
    s = " (Y/n)" if default else " (y/N)"
    try:
        raw = input(message + s + " ").strip().lower()
        if not raw:
            return default
        return raw in ("y", "yes", "1", "true")
    except EOFError:
        return default
