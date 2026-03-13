"""
fix_corpus_state.py — Fix the corrupted corpus_state.json file.

corpus_state.json is a single large JSON object (NOT JSONL).
The previous fix_corpus.py was wrong for this format.

This script:
1. Reads the raw bytes
2. Finds and removes the specific bad control character at char 23,336,583
3. Writes a clean version
4. Verifies it parses correctly

Usage:
    python fix_corpus_state.py
    python fix_corpus_state.py --input output/corpus_state.json --output output/corpus_state_fixed.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def fix_corpus_state(input_path: Path, output_path: Path) -> bool:
    print(f"\n  Reading {input_path}  ({input_path.stat().st_size / 1024 / 1024:.1f} MB)...")

    # Read as bytes first to find the exact bad character
    raw_bytes = input_path.read_bytes()
    print(f"  Total bytes: {len(raw_bytes):,}")

    # Decode with replacement so we can see what's there
    text = raw_bytes.decode("utf-8", errors="replace")
    print(f"  Total chars: {len(text):,}")

    # Show what's at the known bad position
    bad_pos = 23336583
    if bad_pos < len(text):
        context = text[max(0, bad_pos - 20) : bad_pos + 20]
        bad_char = text[bad_pos]
        print(f"\n  Bad char at position {bad_pos}:")
        print(f"    char repr : {repr(bad_char)}")
        print(f"    ord value : {ord(bad_char)}")
        print(f"    context   : {repr(context)}")
    else:
        print(f"  [WARN] Position {bad_pos} is beyond file length {len(text)}")

    # Strategy: remove all illegal control characters from the entire text
    # Legal in JSON strings: \t (0x09), \n (0x0A), \r (0x0D)
    # Illegal: 0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F, 0x7F
    # But inside a JSON string they must be escaped — raw control chars are never valid

    print(f"\n  Scanning for all control characters...")

    control_chars_found: dict[int, int] = {}
    for i, ch in enumerate(text):
        code = ord(ch)
        if (0x00 <= code <= 0x1F or code == 0x7F) and code not in (0x09, 0x0A, 0x0D):
            control_chars_found[code] = control_chars_found.get(code, 0) + 1

    if control_chars_found:
        print(f"  Found control characters:")
        for code, count in sorted(control_chars_found.items()):
            print(f"    0x{code:02X} (\\x{code:02x})  count={count}")
    else:
        print(f"  No illegal control characters found in decoded text")

    # Remove all illegal control characters
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    removed = len(text) - len(cleaned)
    print(f"\n  Removed {removed} illegal control characters")

    # Verify it parses
    print(f"  Verifying JSON parse...")
    try:
        obj = json.loads(cleaned)
        print(f"  ✓ Parses cleanly")

        # Show structure
        if isinstance(obj, dict):
            print(f"  Top-level keys: {list(obj.keys())[:10]}")
            for k, v in obj.items():
                if isinstance(v, dict):
                    print(f"    {k!r}: dict with {len(v)} entries")
                elif isinstance(v, list):
                    print(f"    {k!r}: list with {len(v)} entries")
                else:
                    print(f"    {k!r}: {type(v).__name__} = {str(v)[:50]}")

    except json.JSONDecodeError as e:
        print(f"  ✗ Still fails: {e}")
        print(f"\n  Trying deeper repair...")

        # Try to find remaining bad positions
        for _attempt in range(10):
            m = re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", cleaned)
            if not m:
                break
            pos = m.start()
            print(f"    Found bad char at {pos}: {repr(cleaned[pos])}")
            cleaned = cleaned[:pos] + cleaned[pos + 1 :]

        try:
            obj = json.loads(cleaned)
            print(f"  ✓ Parses after deeper repair")
        except json.JSONDecodeError as e2:
            print(f"  ✗ Cannot repair automatically: {e2}")
            print(f"\n  The file may be truncated or structurally corrupt.")
            print(f"  Recommendation: delete output/corpus_state.json and let it regenerate.")
            return False

    # Write clean version
    print(f"\n  Writing clean file to {output_path}...")
    output_path.write_text(cleaned, encoding="utf-8")
    print(f"  ✓ Written ({output_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # Final verify
    try:
        json.loads(output_path.read_text(encoding="utf-8"))
        print(f"  ✓ Final verification passed")
        return True
    except json.JSONDecodeError as e:
        print(f"  ✗ Final verification failed: {e}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=None, help="Input JSON (default: <project_root>/output/corpus_state.json)")
    ap.add_argument("--output", type=Path, default=None)
    ap.add_argument("--inplace", action="store_true")
    args = ap.parse_args()

    root = _project_root()
    input_path = (args.input if args.input is not None else root / "output" / "corpus_state.json").resolve()

    if not input_path.exists():
        print(f"[ERROR] Not found: {input_path}")
        print(f"\nIf corpus_state.json was overwritten or deleted, the pipeline will regenerate it.")
        print(f"  From project root, run: python main.py  or  python integration/run_complete.py \"text\"")
        print(f"  (Corpus state is created when the full pipeline runs with corpus enabled.)")
        return 1

    if args.inplace:
        output_path = input_path
    elif args.output is not None:
        output_path = args.output.resolve()
    else:
        output_path = input_path.parent / (input_path.stem + "_fixed.json")

    print("=" * 60)
    print("  corpus_state.json Repair")
    print("=" * 60)

    ok = fix_corpus_state(input_path, output_path)

    if ok:
        if output_path != input_path:
            print(f"\n  To use the fixed file:")
            print(f"    Copy-Item {output_path} {input_path} -Force")
        print(f"\n  Then rerun training normally.")
        return 0
    else:
        print(f"\n  ─────────────────────────────────────────────")
        print(f"  SIMPLEST FIX: just delete the file entirely.")
        print(f"  The pipeline regenerates corpus_state.json automatically.")
        print(f"")
        print(f"    Remove-Item output\\corpus_state.json")
        print(f"")
        print(f"  Then rerun training.")
        return 1


def _project_root() -> Path:
    """Project root (directory containing integration/)."""
    script_dir = Path(__file__).resolve().parent
    # integration/model/patch -> go up 3 levels
    return script_dir.parent.parent.parent


if __name__ == "__main__":
    sys.exit(main())
