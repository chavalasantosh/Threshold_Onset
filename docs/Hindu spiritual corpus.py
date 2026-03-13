#!/usr/bin/env python3
"""
Hindu spiritual corpus pipeline for SanTEK (real-source only).

Flow:
1) Download real public-domain texts from source URLs (Project Gutenberg)
2) Clean and split into paragraph samples
3) Build JSONL corpus: data/hindu_corpus_real.jsonl
4) Train SanTEK from that JSONL

No generated text is embedded in this script.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.request
from collections import Counter

# Real public-domain texts (metadata + URL). No text content is hardcoded.
REAL_SOURCES = [
    {
        "id": "gita_arnold_pg2388",
        "title": "The Song Celestial; Or, Bhagavad-Gita",
        "lang": "en",
        "domain": "hinduism",
        "url": "https://www.gutenberg.org/cache/epub/2388/pg2388.txt",
    },
    {
        "id": "upanishads_paramananda_pg3283",
        "title": "The Upanishads",
        "lang": "en",
        "domain": "hinduism",
        "url": "https://www.gutenberg.org/cache/epub/3283/pg3283.txt",
    },
    {
        "id": "light_of_asia_pg8920",
        "title": "The Light of Asia",
        "lang": "en",
        "domain": "indic_spiritual",
        "url": "https://www.gutenberg.org/cache/epub/8920/pg8920.txt",
    },
]

DEFAULT_CORPUS_PATH = "data/hindu_corpus_real.jsonl"
CACHE_DIR = "data/cache"


def _download(url: str, cache_dir: str) -> str:
    """Download URL to cache; return raw text. Stdlib only."""
    os.makedirs(cache_dir, exist_ok=True)
    h = hashlib.sha256(url.encode("utf-8", errors="replace")).hexdigest()[:16]
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in url[-32:])
    path = os.path.join(cache_dir, f"gutenberg_{h}_{safe}.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    req = urllib.request.Request(url, headers={"User-Agent": "THRESHOLD_ONSET/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    with open(path, "w", encoding="utf-8") as f:
        f.write(raw)
    return raw


def _strip_gutenberg_boilerplate(raw: str) -> str:
    """Strip common Gutenberg header/footer markers if present."""
    start_mark = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_mark = "*** END OF THE PROJECT GUTENBERG EBOOK"
    start_idx = raw.find(start_mark)
    end_idx = raw.find(end_mark)
    if start_idx != -1:
        next_nl = raw.find("\n", start_idx)
        if next_nl != -1:
            raw = raw[next_nl + 1 :]
    if end_idx != -1:
        raw = raw[:end_idx]
    return raw


def _paragraphs(raw: str, min_words: int = 8) -> list[str]:
    """Split into non-trivial paragraphs."""
    raw = raw.replace("\r\n", "\n")
    out: list[str] = []
    for p in raw.split("\n\n"):
        s = " ".join(p.strip().split())
        if not s:
            continue
        if len(s.split()) < min_words:
            continue
        out.append(s)
    return out


def _sentence_chunks(raw: str, chunk_sentences: int = 5) -> list[str]:
    """Fallback splitter: chunk text into fixed-size sentence groups."""
    raw = raw.replace("\r\n", "\n")
    flat = " ".join(raw.split())
    parts = re.split(r"(?<=[.!?])\s+", flat)
    parts = [p.strip() for p in parts if p.strip()]
    chunks: list[str] = []
    for i in range(0, len(parts), chunk_sentences):
        chunk = " ".join(parts[i : i + chunk_sentences]).strip()
        if not chunk:
            continue
        w = len(chunk.split())
        if 10 <= w <= 280:
            chunks.append(chunk)
    return chunks


def _to_samples(raw: str) -> list[str]:
    """
    Convert raw source text to many train samples.
    Prefer paragraph split; if too sparse, fallback to sentence chunking.
    """
    paras = _paragraphs(raw, min_words=8)
    # Keep reasonably sized paragraph samples
    paras = [p for p in paras if 10 <= len(p.split()) <= 320]
    if len(paras) >= 30:
        return paras
    # Gutenberg plain text can be formatted with sparse blank lines; fallback.
    chunks = _sentence_chunks(raw, chunk_sentences=5)
    return chunks if chunks else paras


def build_jsonl_from_sources(
    sources: list[dict],
    output_jsonl: str,
    cache_dir: str,
    max_per_source: int | None = None,
) -> tuple[int, Counter]:
    """Download real sources and build JSONL corpus."""
    os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)
    total = 0
    lang_counts: Counter = Counter()
    seen_text_hashes: set[str] = set()

    with open(output_jsonl, "w", encoding="utf-8") as out:
        for src in sources:
            url = src["url"]
            try:
                raw = _download(url, cache_dir)
            except Exception as e:
                print(f"  [warn] Could not download {url[:60]}...: {e}", file=sys.stderr)
                continue
            raw = _strip_gutenberg_boilerplate(raw)
            paras = _to_samples(raw)
            if max_per_source is not None and max_per_source > 0:
                paras = paras[:max_per_source]

            for i, text in enumerate(paras):
                th = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
                if th in seen_text_hashes:
                    continue
                seen_text_hashes.add(th)
                rec = {
                    "id": f"{src['id']}_{i}",
                    "text": text,
                    "lang": src.get("lang", "en"),
                    "domain": src.get("domain", "hinduism"),
                    "title": src.get("title", src["id"]),
                    "source_url": url,
                }
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                total += 1
                lang_counts[rec["lang"]] += 1
    return total, lang_counts


def load_corpus_from_file(path: str) -> list[str]:
    """Load JSONL corpus: one JSON per line with 'text'."""
    texts = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                t = rec.get("text") if isinstance(rec, dict) else None
                if t and isinstance(t, str) and t.strip():
                    texts.append(t.strip())
            except (json.JSONDecodeError, TypeError):
                continue
    return texts


def print_info(source: str, corpus: list[str]):
    total = len(corpus)
    words = sum(len(t.split()) for t in corpus)
    print("=" * 72)
    print("  HINDU CORPUS — real public-domain texts")
    print("=" * 72)
    print(f"  Source          : {source}")
    print(f"  Total texts     : {total}")
    print(f"  Total words     : {words:,}")
    print("=" * 72)


def run_training(corpus: list[str], epochs: int = 300, max_texts: int | None = None):
    import importlib.util

    here = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(here, "..", "santek_base_model.py")
    if not os.path.exists(script_path):
        script_path = os.path.join(here, "santek_base_model.py")
    if not os.path.exists(script_path):
        print("[ERROR] Cannot find santek_base_model.py")
        sys.exit(1)
    script_path = os.path.abspath(script_path)

    spec = importlib.util.spec_from_file_location("santek_base_model", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if max_texts is not None and max_texts > 0:
        corpus = corpus[:max_texts]
        print(f"  Using first {len(corpus)} texts (--max-texts {max_texts})")

    mod.cmd_train(
        corpus=corpus,
        epochs=epochs,
        eta=0.10,
        decay=0.05,
        max_streak=3,
        tension_threshold=0.08,
        patience=7,
        model_path=mod.DEFAULT_MODEL_PATH,
        verbose=True,
    )


def main():
    args = sys.argv[1:]
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_dir = os.path.join(repo, CACHE_DIR)

    use_file = None
    out_jsonl = os.path.join(repo, DEFAULT_CORPUS_PATH)
    if "--corpus-file" in args:
        idx = args.index("--corpus-file")
        if idx + 1 < len(args):
            use_file = os.path.abspath(args[idx + 1])
    if "--output-jsonl" in args:
        idx = args.index("--output-jsonl")
        if idx + 1 < len(args):
            out_jsonl = os.path.abspath(args[idx + 1])

    if "--build-jsonl" in args:
        max_per_source = None
        if "--max-per-source" in args:
            idx = args.index("--max-per-source")
            if idx + 1 < len(args):
                try:
                    max_per_source = int(args[idx + 1])
                except ValueError:
                    pass
        total, lang_counts = build_jsonl_from_sources(
            REAL_SOURCES, out_jsonl, cache_dir, max_per_source=max_per_source
        )
        print(f"Built JSONL corpus: {out_jsonl}")
        print(f"Total records: {total}")
        print(f"Language counts: {dict(lang_counts)}")
        if "--train-after-build" not in args:
            return

    if use_file:
        if not os.path.exists(use_file):
            print("[ERROR] Corpus file not found:", use_file)
            sys.exit(1)
        corpus = load_corpus_from_file(use_file)
        source = use_file
    else:
        if not os.path.exists(out_jsonl):
            total, _ = build_jsonl_from_sources(REAL_SOURCES, out_jsonl, cache_dir, max_per_source=None)
            print(f"Built JSONL corpus at {out_jsonl} with {total} records.")
        corpus = load_corpus_from_file(out_jsonl)
        source = out_jsonl

    if not corpus:
        print("[ERROR] No texts loaded.")
        sys.exit(1)

    if "--info" in args:
        print_info(source, corpus)
        sys.exit(0)

    epochs = 300
    max_texts = None
    if "--epochs" in args:
        idx = args.index("--epochs")
        if idx + 1 < len(args):
            try:
                epochs = int(args[idx + 1])
            except ValueError:
                pass
    if "--max-texts" in args:
        idx = args.index("--max-texts")
        if idx + 1 < len(args):
            try:
                max_texts = int(args[idx + 1])
            except ValueError:
                pass
    if "--quick" in args:
        max_texts = 40
        epochs = 40
        print("  [--quick] max_texts=40 epochs=40")
    if "--minimal" in args:
        max_texts = 10
        epochs = 15
        print("  [--minimal] max_texts=10 epochs=15")

    print_info(source, corpus)
    print()
    n = min(len(corpus), max_texts) if max_texts else len(corpus)
    print(f"Training on {n} texts for {epochs} epochs...")
    run_training(corpus, epochs=epochs, max_texts=max_texts)


if __name__ == "__main__":
    main()
