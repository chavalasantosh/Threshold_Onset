"""
fix_single_json.py — Repair a single JSON file (one document) with invalid control characters.

Use this for output/corpus_state.json and other single-document JSON files.
Do NOT use fix_corpus.py for these — fix_corpus.py is for JSONL (one JSON per line).

Usage:
  python fix_single_json.py --input output/corpus_state.json --output output/corpus_state_fixed.json
  python fix_single_json.py --input output/corpus_state.json   (writes to <input>_fixed.json)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Control chars that break JSON when unescaped inside strings (keep tab, newline, carriage return)
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def repair_json_text(raw: str) -> str:
    """Replace unescaped control characters so the string can be parsed as JSON."""
    return CONTROL_CHAR_RE.sub(" ", raw)


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair single JSON file (control characters).")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file path")
    parser.add_argument("--output", "-o", help="Output path (default: <input>_fixed.json)")
    parser.add_argument("--inplace", action="store_true", help="Overwrite input (after successful parse)")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print(f"[ERROR] File not found: {inp}", file=sys.stderr)
        return 1

    raw = inp.read_text(encoding="utf-8", errors="replace")
    repaired = repair_json_text(raw)

    try:
        data = json.loads(repaired)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Still invalid JSON after repair: {e}", file=sys.stderr)
        return 1

    out_path = Path(args.output) if args.output else inp.parent / f"{inp.stem}_fixed.json"
    if args.inplace:
        out_path = inp

    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Repaired JSON written to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
