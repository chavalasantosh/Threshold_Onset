"""
download_ai4bharat.py — Download AI4Bharat Sangraha with correct API.

The main bulk_download.py used wrong parameter (lang=).
Sangraha uses the language code directly as the split name.

Correct codes:
  tel = Telugu
  hin = Hindi
  tam = Tamil
  san = Sanskrit
  eng = English

Usage:
  python download_ai4bharat.py
  python download_ai4bharat.py --languages tel hin tam san
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

BULK_DIR = Path("data/bulk")
SHARD_SIZE = 100_000
MIN_TEXT_LEN = 30
MAX_TEXT_LEN = 10_000

# Mapping from 2-letter to 3-letter codes used by sangraha
LANG_MAP = {
    "te": "tel",
    "hi": "hin",
    "ta": "tam",
    "sa": "san",
    "en": "eng",
    # also accept 3-letter directly
    "tel": "tel",
    "hin": "hin",
    "tam": "tam",
    "san": "san",
    "eng": "eng",
}

DISPLAY = {
    "tel": "Telugu",
    "hin": "Hindi",
    "tam": "Tamil",
    "san": "Sanskrit",
    "eng": "English",
}


def _make_id(source: str, index: int, text: str) -> str:
    h = hashlib.md5(text[:100].encode("utf-8", errors="replace")).hexdigest()[:8]
    return f"{source}_{index:08d}_{h}"


def _clean(text: str) -> str:
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _already_downloaded(source: str) -> int:
    d = BULK_DIR / source
    if not d.exists():
        return 0
    return sum(
        sum(1 for _ in open(f, encoding="utf-8"))
        for f in d.glob("shard_*.jsonl")
    )


def download_sangraha(lang_3: str, split: str = "verified") -> int:
    """Download one language from AI4Bharat Sangraha. Returns record count."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("  pip install datasets")
        return 0

    source = f"ai4bharat_{lang_3}"
    existing = _already_downloaded(source)
    if existing > 0:
        print(f"  [SKIP] {source} already has {existing:,} records")
        return existing

    print(f"\n  Downloading AI4Bharat Sangraha — {DISPLAY.get(lang_3, lang_3)} ({lang_3})...")

    out_dir = BULK_DIR / source
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Correct API: split = language code (tel, hin, tam, san)
        ds = load_dataset(
            "ai4bharat/sangraha",
            split,          # "verified" config
            split=lang_3,   # language as split name
        )
    except Exception as e:
        print(f"  [ERROR] verified/{lang_3}: {e}")
        # Try unverified
        try:
            ds = load_dataset(
                "ai4bharat/sangraha",
                "unverified",
                split=lang_3,
            )
            print(f"  Using unverified split for {lang_3}")
        except Exception as e2:
            print(f"  [ERROR] unverified/{lang_3}: {e2}")
            return 0

    shard_idx = 0
    buffer = []
    total = 0

    def flush():
        nonlocal shard_idx, total
        if not buffer:
            return
        path = out_dir / f"shard_{shard_idx:05d}.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for rec in buffer:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        total += len(buffer)
        print(f"    ✓ Shard {shard_idx:05d} → {path.name}  ({len(buffer):,} records, total={total:,})")
        shard_idx += 1
        buffer.clear()

    for i, row in enumerate(ds):
        text = _clean(str(row.get("text", "") or row.get("sentence", "")))
        if len(text) < MIN_TEXT_LEN:
            continue
        buffer.append({
            "id": _make_id(source, i, text),
            "text": text[:MAX_TEXT_LEN],
            "lang": lang_3[:2],   # back to 2-letter for pipeline compatibility
            "domain": "ai4bharat_sangraha",
        })
        if len(buffer) >= SHARD_SIZE:
            flush()
        if i % 500_000 == 0 and i > 0:
            print(f"    Processed: {i:,}")

    flush()
    print(f"  ✓ {DISPLAY.get(lang_3, lang_3)}: {total:,} records")
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--languages", nargs="+",
                    default=["tel", "hin", "tam", "san"],
                    help="3-letter lang codes: tel hin tam san eng")
    ap.add_argument("--split", default="verified", choices=["verified", "unverified"])
    args = ap.parse_args()

    print("\n" + "=" * 55)
    print("  AI4Bharat Sangraha Downloader (fixed API)")
    print("=" * 55)

    grand_total = 0
    for lang in args.languages:
        lang_3 = LANG_MAP.get(lang, lang)
        count = download_sangraha(lang_3, args.split)
        grand_total += count

    print(f"\n  Total downloaded: {grand_total:,} records")
    print(f"\n  Now merge:")
    print(f"    python integration/model/bulk_download.py --merge --output data/hindu_corpus_mega.jsonl")


if __name__ == "__main__":
    main()