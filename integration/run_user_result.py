#!/usr/bin/env python3
"""
End-user result only: run pipeline and show INPUT + OUTPUT.

Usage:
  py integration/run_user_result.py "I am Eating"
  py integration/run_user_result.py
  echo "Your text" | py integration/run_user_result.py

Shows only the end-user outcome, without technical steps.
"""

import sys
import contextlib
import io
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Must set argv before importing run_complete (it reads sys.argv for input)
if len(sys.argv) > 1:
    pass  # User provided args
elif not sys.stdin.isatty():
    stdin_text = sys.stdin.read().strip()
    sys.argv = [sys.argv[0], stdin_text]
else:
    # Interactive: prompt so user can type or paste without quoting on CLI
    try:
        from integration.interactive_prompt import prompt_text
        text = prompt_text("Enter your text (press Enter twice when done):")
    except ImportError:
        print("Enter your text (press Enter twice when done):")
        lines = []
        try:
            while True:
                line = input("> " if not lines else "... ")
                if line == "" and lines:
                    break
                if line != "":
                    lines.append(line)
        except EOFError:
            pass
        text = "\n".join(lines).strip() if lines else ""
    if not text:
        print("No text entered. Run: py run_user_result.py \"Your text\"  or run without args and type when asked.")
        sys.exit(1)
    sys.argv = [sys.argv[0], text]

# Suppress all pipeline output, run, get result
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "run_complete", project_root / "integration" / "run_complete.py"
)
_run_complete = importlib.util.module_from_spec(_spec)
# Required so dataclasses inside run_complete can resolve cls.__module__ (Python 3.13)
sys.modules["run_complete"] = _run_complete
_spec.loader.exec_module(_run_complete)

with contextlib.redirect_stdout(io.StringIO()):
    result = _run_complete.run(return_result=True, return_model_state=False)

if result is None:
    print("Error: Pipeline failed.")
    sys.exit(1)

# result is PipelineResult (dataclass)
_run_complete.TUIRenderer(show_tui=True).end_user_result(result)
