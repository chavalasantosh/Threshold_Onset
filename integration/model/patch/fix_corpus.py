"""
fix_corpus.py — Repair the corrupted JSONL corpus file.

PROBLEM (from run logs):
  Corpus state init failed (disabling): Invalid control character at: line 149367 column 89 (char 23336583)
  Corpus state init failed (disabling): Expecting ':' delimiter: line 64206 column 136 (char 9909288)

These are JSON parse errors from control characters (null bytes, unescaped newlines,
carriage returns inside JSON strings) in the corpus JSONL file.

This script:
  1. Scans the entire corpus JSONL
  2. Reports all bad lines
  3. Writes a clean version with all bad lines repaired
  4. Verifies the clean file loads without errors

Usage:
  python fix_corpus.py --input data/hindu_corpus_real.jsonl
  python fix_corpus.py --input data/hindu_corpus_real.jsonl --output data/hindu_corpus_clean.jsonl
  python fix_corpus.py --input data/hindu_corpus_real.jsonl --verify-only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Tuple


# Control characters that break JSON parsing (except \t \n \r which are legal in strings
# only when properly escaped — raw bytes are not)
CONTROL_CHAR_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')


def _clean_text(text: str) -> str:
    """
    Remove or replace illegal control characters from a string.
    - Null bytes (\\x00): remove entirely
    - Other control chars: replace with space
    - Raw \\n / \\r inside a JSON string value: these appear as literal newlines
      in the text field, which is fine; json.dumps will escape them properly.
    """
    # Remove null bytes
    text = text.replace('\x00', '')
    # Replace other control chars with space
    text = CONTROL_CHAR_RE.sub(' ', text)
    # Normalize multiple spaces
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def scan_and_repair(
    input_path: Path,
    output_path: Path | None = None,
    verbose: bool = True,
) -> Tuple[int, int, int]:
    """
    Scan input JSONL, repair bad lines, write clean output.
    Returns (total_lines, bad_lines_fixed, skipped_lines).
    """
    total = 0
    fixed = 0
    skipped = 0
    clean_records: List[str] = []

    with open(input_path, encoding='utf-8', errors='replace') as f:
        for lineno, raw_line in enumerate(f, 1):
            total += 1
            line = raw_line.rstrip('\n\r')
            if not line.strip():
                continue

            # Try parsing as-is first
            try:
                obj = json.loads(line)
                clean_records.append(json.dumps(obj, ensure_ascii=False))
                continue
            except json.JSONDecodeError:
                pass

            # Attempt repair
            repaired = False

            # Strategy 1: strip control characters from the raw line then re-parse
            cleaned_line = CONTROL_CHAR_RE.sub('', line)
            cleaned_line = cleaned_line.replace('\x00', '')
            try:
                obj = json.loads(cleaned_line)
                # Also clean text field specifically
                if 'text' in obj:
                    obj['text'] = _clean_text(str(obj['text']))
                clean_records.append(json.dumps(obj, ensure_ascii=False))
                fixed += 1
                repaired = True
                if verbose and fixed <= 20:
                    print(f"  [FIXED]   line {lineno:>8}  (control char removal)")
            except json.JSONDecodeError:
                pass

            if repaired:
                continue

            # Strategy 2: try to extract text field with regex if JSON is malformed
            text_match = re.search(r'"text"\s*:\s*"((?:[^"\\]|\\.)*)"', line)
            id_match = re.search(r'"id"\s*:\s*"([^"]*)"', line)
            lang_match = re.search(r'"lang"\s*:\s*"([^"]*)"', line)

            if text_match:
                text_val = text_match.group(1)
                # Unescape basic JSON escapes
                try:
                    text_val = bytes(text_val, 'utf-8').decode('unicode_escape')
                except Exception:
                    pass
                text_val = _clean_text(text_val)
                obj = {
                    'id': id_match.group(1) if id_match else f'repaired_{lineno}',
                    'text': text_val,
                    'lang': lang_match.group(1) if lang_match else 'unknown',
                }
                clean_records.append(json.dumps(obj, ensure_ascii=False))
                fixed += 1
                repaired = True
                if verbose and fixed <= 20:
                    print(f"  [FIXED]   line {lineno:>8}  (regex extraction)")

            if not repaired:
                skipped += 1
                if verbose and skipped <= 10:
                    print(f"  [SKIPPED] line {lineno:>8}  (unrecoverable): {line[:80]!r}")

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            for rec in clean_records:
                f.write(rec + '\n')
        print(f"\n  Written: {output_path}  ({len(clean_records):,} records)")

    return total, fixed, skipped


def verify_corpus(path: Path) -> Tuple[bool, int, List[Tuple[int, str]]]:
    """
    Verify every line in the corpus parses cleanly.
    Returns (all_ok, total_records, [(lineno, error), ...])
    """
    errors: List[Tuple[int, str]] = []
    total = 0
    with open(path, encoding='utf-8', errors='replace') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                errors.append((lineno, str(e)))
                if len(errors) >= 20:
                    errors.append((-1, f"... (stopped after 20 errors)"))
                    break
    return len(errors) == 0, total, errors


def main():
    ap = argparse.ArgumentParser(description="Repair corrupted JSONL corpus for SanTEK")
    ap.add_argument('--input', type=Path, required=True, help='Input JSONL corpus path')
    ap.add_argument('--output', type=Path, default=None,
                    help='Output clean JSONL path (default: input_clean.jsonl)')
    ap.add_argument('--verify-only', action='store_true',
                    help='Only verify the file, do not repair')
    ap.add_argument('--inplace', action='store_true',
                    help='Overwrite input file with repaired version')
    args = ap.parse_args()

    if not args.input.exists():
        print(f"[ERROR] Input file not found: {args.input}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  SanTEK Corpus Repair Tool")
    print(f"{'='*60}")
    print(f"  Input : {args.input}")
    print(f"  Size  : {args.input.stat().st_size / 1024 / 1024:.1f} MB")

    if args.verify_only:
        print(f"\n  Verifying...")
        ok, total, errors = verify_corpus(args.input)
        print(f"  Total records : {total:,}")
        if ok:
            print(f"  Result        : ✓ ALL CLEAN — no JSON errors found")
        else:
            print(f"  Result        : ✗ {len(errors)} errors found")
            for lineno, err in errors[:10]:
                if lineno == -1:
                    print(f"    {err}")
                else:
                    print(f"    line {lineno:>8}: {err}")
        return

    # Determine output path
    if args.inplace:
        output_path = args.input
        print(f"  Output: {output_path}  (IN-PLACE)")
    elif args.output:
        output_path = args.output
        print(f"  Output: {output_path}")
    else:
        stem = args.input.stem
        output_path = args.input.parent / f"{stem}_clean.jsonl"
        print(f"  Output: {output_path}  (auto-named)")

    print(f"\n  Scanning and repairing...")
    total, fixed, skipped = scan_and_repair(args.input, output_path, verbose=True)

    print(f"\n  {'─'*50}")
    print(f"  Total lines scanned : {total:,}")
    print(f"  Lines fixed         : {fixed:,}")
    print(f"  Lines skipped       : {skipped:,}")
    print(f"  Clean records       : {total - skipped:,}")

    # Verify the output
    print(f"\n  Verifying output...")
    ok, total_out, errors = verify_corpus(output_path)
    if ok:
        print(f"  ✓ Output is clean — {total_out:,} records, 0 JSON errors")
    else:
        print(f"  ✗ {len(errors)} errors remain in output:")
        for lineno, err in errors[:5]:
            print(f"    line {lineno}: {err}")

    print(f"\n  Done.")
    if not args.inplace:
        print(f"\n  Next step: update your build_hindu_corpus.py to point to:")
        print(f"    {output_path}")
        print(f"  Or rename it to replace the original.")


if __name__ == '__main__':
    main()
