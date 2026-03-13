#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_hindu_corpus.py
═══════════════════════════════════════════════════════════════════════════════
THRESHOLD_ONSET — Hindu Corpus Downloader + Training Pipeline
Author : Chavala Santosh
Project: THRESHOLD_ONSET / SanTEK Base Model

What this script does
─────────────────────
STEP 1 — DOWNLOAD
  Downloads real Hindu sacred texts from public domain sources:
  - Project Gutenberg (Bhagavad Gita, Upanishads, Vedic Hymns, Mahabharata,
    Ramayana, Yoga Sutras, Hindu literature)
  - Wikisource plain text exports (Sanskrit, Telugu, Hindi, Tamil)
  - GRETIL-compatible public URLs
  - Saves every text as a real .txt file under data/raw/<language>/

STEP 2 — CLEAN
  Cleans each downloaded file:
  - Removes Project Gutenberg headers/footers
  - Splits into paragraphs / verses
  - Filters too-short or too-long segments
  - Saves cleaned segments to data/clean/<source>.jsonl

STEP 3 — BUILD CORPUS
  Merges all cleaned JSONL files into one master:
  data/hindu_corpus_real.jsonl
  Each line: {"text": "...", "lang": "en", "source": "bhagavad_gita", "file": "bhagavad_gita_arnold"}

STEP 4 — TRAIN
  Reads data/hindu_corpus_real.jsonl and runs santek_base_model.py training.
  --epochs, --eta, --decay flags pass through.

Languages targeted
──────────────────
  Sanskrit (romanized + Devanagari) | English | Telugu | Hindi | Tamil

Usage
─────
  # Full pipeline (download + clean + build + train):
  python build_hindu_corpus.py

  # Only download + clean (skip training):
  python build_hindu_corpus.py --no-train

  # Only train on existing data/hindu_corpus_real.jsonl:
  python build_hindu_corpus.py --only-train

  # Custom epochs:
  python build_hindu_corpus.py --epochs 500

  # Limit corpus size for testing:
  python build_hindu_corpus.py --max-texts 200 --epochs 50

  # Rebuild corpus with paragraph-sized segments (30–200 words), then train:
  python build_hindu_corpus.py --download-only
  python build_hindu_corpus.py --skip-download --epochs 2500

═══════════════════════════════════════════════════════════════════════════════
ZERO third-party libraries. Pure Python stdlib only.
urllib.request  |  json  |  pathlib  |  re  |  time  |  argparse
═══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ─── Paths ────────────────────────────────────────────────────────────────────

HERE = Path(__file__).parent.resolve()


def _repo_root() -> Path:
    """Use repo root for data so data/ is shared whether script runs from root or docs/."""
    for candidate in [HERE, HERE.parent]:
        if (candidate / "santek_base_model.py").exists():
            return candidate
        if (candidate / "integration" / "run_complete.py").exists():
            return candidate
    return HERE


REPO_ROOT = _repo_root()
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
CORPUS_FILE = DATA_DIR / "hindu_corpus_real.jsonl"
OUTPUT_DIR = REPO_ROOT / "output"

for _d in [RAW_DIR, CLEAN_DIR, OUTPUT_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# ─── Terminal colours (no rich, no curses) ────────────────────────────────────

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"

def OK(msg):   print(_c("32", "  ✓ ") + msg)
def INFO(msg): print(_c("36", "  ▸ ") + msg)
def WARN(msg): print(_c("33", "  ⚠ ") + msg)
def ERR(msg):  print(_c("31", "  ✗ ") + msg)
def HEAD(msg): print("\n" + _c("1;35", "══ " + msg + " " + "═" * max(0, 60 - len(msg))))

# ─── Download helpers ─────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; HinduCorpusBuilder/1.0; "
        "+https://github.com/chavalasantosh/Threshold_Onset)"
    )
}

def fetch_url(url: str, retries: int = 3, delay: float = 2.0) -> Optional[str]:
    """Download URL → string. Returns None on failure."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                # Try UTF-8 first, then latin-1
                for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
                    try:
                        return raw.decode(enc)
                    except UnicodeDecodeError:
                        continue
                return raw.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            WARN(f"HTTP {e.code} on {url[:70]}  (attempt {attempt+1}/{retries})")
            if e.code in (403, 404, 410):
                return None  # permanent failure
        except Exception as e:
            WARN(f"Error on {url[:70]}: {e}  (attempt {attempt+1}/{retries})")
        if attempt < retries - 1:
            time.sleep(delay * (attempt + 1))
    return None

def save_raw(name: str, lang: str, text: str) -> Path:
    """Save raw downloaded text."""
    lang_dir = RAW_DIR / lang
    lang_dir.mkdir(parents=True, exist_ok=True)
    path = lang_dir / f"{name}.txt"
    path.write_text(text, encoding="utf-8")
    return path

# ─── Gutenberg stripper ───────────────────────────────────────────────────────

_GB_START = re.compile(
    r"\*{3}\s*START OF (THIS|THE) PROJECT GUTENBERG.*?\*{3}", re.IGNORECASE
)
_GB_END = re.compile(
    r"\*{3}\s*END OF (THIS|THE) PROJECT GUTENBERG.*?\*{3}", re.IGNORECASE
)

def strip_gutenberg(text: str) -> str:
    """Remove Project Gutenberg header and footer."""
    m_start = _GB_START.search(text)
    m_end   = _GB_END.search(text)
    if m_start:
        text = text[m_start.end():]
    if m_end:
        text = text[:m_end.start()]
    return text.strip()

# ─── Text splitter ────────────────────────────────────────────────────────────

def split_into_segments(
    text: str,
    min_words: int = 150,
    max_words: int = 999,
) -> List[str]:
    """
    Split cleaned text into training segments (paragraph-sized, not single sentences).
    Strategy:
      1. Split on double newlines (paragraphs).
      2. If a paragraph is too long, split on single newlines.
      3. If still too long, split on sentence boundaries (. ! ?).
      4. Discard segments that are too short (< min_words) or too long (> max_words).
    Target: 60–200 words per segment so the symbol graph can grow (not ~11 words).
    """
    # Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Split on paragraph breaks
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]

    segments = []
    for para in paragraphs:
        words = para.split()
        if len(words) <= max_words:
            if len(words) >= min_words:
                segments.append(" ".join(words))
        else:
            # Split on single newlines first
            lines = [l.strip() for l in para.split("\n") if l.strip()]
            for line in lines:
                w = line.split()
                if len(w) >= min_words and len(w) <= max_words:
                    segments.append(" ".join(w))
                elif len(w) > max_words:
                    # Split on sentence boundary
                    sents = re.split(r"(?<=[.!?])\s+", line)
                    buf = []
                    for sent in sents:
                        sw = sent.split()
                        if len(buf) + len(sw) <= max_words:
                            buf.extend(sw)
                        else:
                            if len(buf) >= min_words:
                                segments.append(" ".join(buf))
                            buf = sw
                    if len(buf) >= min_words:
                        segments.append(" ".join(buf))

    return segments

# ─────────────────────────────────────────────────────────────────────────────
# SOURCE CATALOGUE
# Every entry: (name, lang, url, source_tag)
# ─────────────────────────────────────────────────────────────────────────────

SOURCES: List[Tuple[str, str, str, str]] = [

    # ── BHAGAVAD GITA ─────────────────────────────────────────────────────────
    (
        "bhagavad_gita_arnold",
        "en",
        "https://www.gutenberg.org/cache/epub/2388/pg2388.txt",
        "bhagavad_gita",
    ),
    (
        "bhagavad_gita_telugu",
        "te",
        "https://www.sacred-texts.com/hin/gita/gita.htm",
        "bhagavad_gita",
    ),

    # ── UPANISHADS ────────────────────────────────────────────────────────────
    (
        "upanishads_paramananda",
        "en",
        "https://www.gutenberg.org/cache/epub/3283/pg3283.txt",
        "upanishads",
    ),
    (
        "upanishads_muller",
        "en",
        "https://www.gutenberg.org/cache/epub/1163/pg1163.txt",
        "upanishads",
    ),
    (
        "upanishads_fifteen",
        "en",
        "https://www.gutenberg.org/cache/epub/3924/pg3924.txt",
        "upanishads",
    ),

    # ── VEDIC HYMNS ───────────────────────────────────────────────────────────
    (
        "vedic_hymns_griffith",
        "en",
        "https://www.gutenberg.org/cache/epub/12894/pg12894.txt",
        "rigveda",
    ),
    (
        "hymns_atharva_veda",
        "en",
        "https://www.gutenberg.org/cache/epub/16295/pg16295.txt",
        "atharva_veda",
    ),

    # ── MAHABHARATA ───────────────────────────────────────────────────────────
    (
        "mahabharata_ganguli_1",
        "en",
        "https://www.gutenberg.org/cache/epub/15474/pg15474.txt",
        "mahabharata",
    ),
    (
        "mahabharata_ganguli_2",
        "en",
        "https://www.gutenberg.org/cache/epub/15476/pg15476.txt",
        "mahabharata",
    ),
    (
        "mahabharata_ganguli_3",
        "en",
        "https://www.gutenberg.org/cache/epub/15477/pg15477.txt",
        "mahabharata",
    ),
    (
        "mahabharata_ganguli_4",
        "en",
        "https://www.gutenberg.org/cache/epub/15478/pg15478.txt",
        "mahabharata",
    ),
    (
        "mahabharata_ganguli_5",
        "en",
        "https://www.gutenberg.org/cache/epub/15479/pg15479.txt",
        "mahabharata",
    ),

    # ── RAMAYANA ──────────────────────────────────────────────────────────────
    (
        "ramayana_griffith",
        "en",
        "https://www.gutenberg.org/cache/epub/24869/pg24869.txt",
        "ramayana",
    ),
    (
        "ramayana_prose",
        "en",
        "https://www.gutenberg.org/cache/epub/7864/pg7864.txt",
        "ramayana",
    ),

    # ── YOGA & PHILOSOPHY ─────────────────────────────────────────────────────
    (
        "yoga_sutras_johnston",
        "en",
        "https://www.gutenberg.org/cache/epub/20705/pg20705.txt",
        "yoga_sutras",
    ),
    (
        "light_of_asia_arnold",
        "en",
        "https://www.gutenberg.org/cache/epub/8920/pg8920.txt",
        "hindu_philosophy",
    ),
    (
        "vedanta_philosophy",
        "en",
        "https://www.gutenberg.org/cache/epub/22544/pg22544.txt",
        "vedanta",
    ),
    (
        "hindu_philosophy_muller",
        "en",
        "https://www.gutenberg.org/cache/epub/24038/pg24038.txt",
        "vedanta",
    ),

    # ── PURANAS ───────────────────────────────────────────────────────────────
    (
        "vishnu_purana_wilson",
        "en",
        "https://www.gutenberg.org/cache/epub/16542/pg16542.txt",
        "vishnu_purana",
    ),
    (
        "garuda_purana",
        "en",
        "https://www.sacred-texts.com/hin/gpu/gpu00.htm",
        "garuda_purana",
    ),

    # ── TAMIL — THIRUKKURAL ──────────────────────────────────────────────────
    (
        "thirukkural_tamil",
        "ta",
        "https://www.gutenberg.org/cache/epub/34451/pg34451.txt",
        "thirukkural",
    ),
    (
        "thirukkural_english",
        "en",
        "https://www.gutenberg.org/cache/epub/35788/pg35788.txt",
        "thirukkural",
    ),

    # ── HINDI DEVOTIONAL ──────────────────────────────────────────────────────
    (
        "tulsidas_ramcharitmanas_en",
        "en",
        "https://www.sacred-texts.com/hin/rama/index.htm",
        "ramcharitmanas",
    ),

    # ── SACRED TEXTS FALLBACKS ────────────────────────────────────────────────
    (
        "rig_veda_sacred",
        "en",
        "https://www.sacred-texts.com/hin/rigveda/rvi01.htm",
        "rigveda",
    ),
    (
        "upanishads_sacred",
        "en",
        "https://www.sacred-texts.com/hin/upan/index.htm",
        "upanishads",
    ),
    (
        "chandogya_upanishad",
        "en",
        "https://www.gutenberg.org/cache/epub/17925/pg17925.txt",
        "upanishads",
    ),

    # ── VEDANTA TEXTS ─────────────────────────────────────────────────────────
    (
        "vivekachudamani_shankaracharya",
        "en",
        "https://www.gutenberg.org/cache/epub/22175/pg22175.txt",
        "vedanta",
    ),
    (
        "jnana_yoga_vivekananda",
        "en",
        "https://www.gutenberg.org/cache/epub/2105/pg2105.txt",
        "vivekananda",
    ),
    (
        "raja_yoga_vivekananda",
        "en",
        "https://www.gutenberg.org/cache/epub/2204/pg2204.txt",
        "vivekananda",
    ),
    (
        "bhakti_yoga_vivekananda",
        "en",
        "https://www.gutenberg.org/cache/epub/2245/pg2245.txt",
        "vivekananda",
    ),
    (
        "karma_yoga_vivekananda",
        "en",
        "https://www.gutenberg.org/cache/epub/2247/pg2247.txt",
        "vivekananda",
    ),
    (
        "complete_works_vivekananda",
        "en",
        "https://www.gutenberg.org/cache/epub/22515/pg22515.txt",
        "vivekananda",
    ),

    # ── MORE UPANISHADS ───────────────────────────────────────────────────────
    (
        "kena_katha_upanishad",
        "en",
        "https://www.gutenberg.org/cache/epub/19360/pg19360.txt",
        "upanishads",
    ),
    (
        "mandukya_upanishad",
        "en",
        "https://www.gutenberg.org/cache/epub/18957/pg18957.txt",
        "upanishads",
    ),

    # ── SANSKRIT TEXTS ────────────────────────────────────────────────────────
    (
        "sankhya_karika",
        "en",
        "https://www.gutenberg.org/cache/epub/22454/pg22454.txt",
        "sankhya",
    ),
    (
        "dharmasutras",
        "en",
        "https://www.gutenberg.org/cache/epub/26697/pg26697.txt",
        "dharmashastra",
    ),
    (
        "manusmriti_en",
        "en",
        "https://www.gutenberg.org/cache/epub/17321/pg17321.txt",
        "dharmashastra",
    ),

    # ── DEVOTIONAL LITERATURE ─────────────────────────────────────────────────
    (
        "narada_bhakti_sutras",
        "en",
        "https://www.gutenberg.org/cache/epub/25726/pg25726.txt",
        "bhakti",
    ),
    (
        "hymns_of_tamil_saints",
        "en",
        "https://www.sacred-texts.com/hin/sha/index.htm",
        "tamil_saints",
    ),
    (
        "songs_of_kabir",
        "en",
        "https://www.gutenberg.org/cache/epub/6768/pg6768.txt",
        "bhakti",
    ),
    (
        "hymns_shankara",
        "en",
        "https://www.gutenberg.org/cache/epub/26805/pg26805.txt",
        "vedanta",
    ),

    # ── ITIHASA & DHARMA ─────────────────────────────────────────────────────
    (
        "arthashastra_kautilya",
        "en",
        "https://www.gutenberg.org/cache/epub/15184/pg15184.txt",
        "dharmashastra",
    ),
    (
        "panchatantra_ryder",
        "en",
        "https://www.gutenberg.org/cache/epub/7100/pg7100.txt",
        "stories",
    ),
    (
        "kathasaritsagara",
        "en",
        "https://www.gutenberg.org/cache/epub/21451/pg21451.txt",
        "stories",
    ),
]

# ─── HTML stripper ────────────────────────────────────────────────────────────

def strip_html(html: str) -> str:
    """Remove HTML tags and decode basic entities."""
    # Remove scripts and styles entirely
    html = re.sub(r"<(script|style)[^>]*>.*?</(script|style)>", " ",
                  html, flags=re.IGNORECASE | re.DOTALL)
    # Remove tags
    html = re.sub(r"<[^>]+>", " ", html)
    # Decode entities
    entities = {
        "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"',
        "&apos;": "'", "&nbsp;": " ", "&#39;": "'", "&mdash;": "—",
        "&ndash;": "–", "&ldquo;": '"', "&rdquo;": '"',
        "&lsquo;": "'", "&rsquo;": "'",
    }
    for ent, rep in entities.items():
        html = html.replace(ent, rep)
    # Decode numeric entities
    html = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), html)
    # Collapse whitespace
    html = re.sub(r"[ \t]+", " ", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()

# ─── Noise filter ─────────────────────────────────────────────────────────────

_NOISE_PATTERNS = [
    re.compile(r"^\s*page\s+\d+\s*$", re.IGNORECASE),
    re.compile(r"^\s*\[?\d+\]?\s*$"),
    re.compile(r"^\s*[-–—=*#~_]{3,}\s*$"),
    re.compile(r"produced by", re.IGNORECASE),
    re.compile(r"project gutenberg", re.IGNORECASE),
    re.compile(r"transcribed by", re.IGNORECASE),
    re.compile(r"scanned by", re.IGNORECASE),
    re.compile(r"http[s]?://\S+"),
    re.compile(r"^\s*\[.*?\]\s*$"),
    re.compile(r"^\s*note\s*:", re.IGNORECASE),
    re.compile(r"this ebook is for the use of anyone", re.IGNORECASE),
    # Gutenberg header/footer — drop any segment containing these (fixes Problem 2)
    re.compile(r"\*\*\*?\s*END\s+OF\s+(THIS|THE)\s+PROJECT\s+GUTENBERG", re.IGNORECASE),
    re.compile(r"\*\*\*?\s*START\s+OF\s+(THIS|THE)\s+PROJECT\s+GUTENBERG", re.IGNORECASE),
    re.compile(r"end of the project gutenberg ebook", re.IGNORECASE),
    re.compile(r"start of the project gutenberg ebook", re.IGNORECASE),
]

def is_noise(segment: str) -> bool:
    for pat in _NOISE_PATTERNS:
        if pat.search(segment):
            return True
    words = segment.split()
    if len(words) > 0:
        num_count = sum(1 for w in words if re.match(r"^\d+\.?$", w))
        if num_count / len(words) > 0.4:
            return True
    return False

# ─── STEP 1 + 2: Download and clean ──────────────────────────────────────────

def download_and_clean_all(
    sources: List[Tuple[str, str, str, str]],
    skip_existing: bool = True,
) -> Dict[str, List[Dict]]:
    """
    Download each source, clean it, split into segments.
    Returns dict: source_tag → list of {"text":..., "lang":..., "source":...}
    """
    HEAD("STEP 1 — DOWNLOADING HINDU SACRED TEXTS")
    print(f"  Targets: {len(sources)} sources")
    print(f"  Raw  → {RAW_DIR}")
    print(f"  Clean→ {CLEAN_DIR}")

    all_records: Dict[str, List[Dict]] = {}
    success_count = 0
    fail_count    = 0

    for idx, (name, lang, url, source_tag) in enumerate(sources, 1):
        raw_path   = RAW_DIR / lang / f"{name}.txt"
        clean_path = CLEAN_DIR / f"{name}.jsonl"

        print(f"\n  [{idx:02d}/{len(sources)}] {name}  ({lang})")
        INFO(f"URL: {url[:80]}")

        # ── Load raw ─────────────────────────────────────────────────────────
        if skip_existing and raw_path.exists() and raw_path.stat().st_size > 500:
            INFO("Raw file exists — skipping download")
            raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
        else:
            INFO("Downloading...")
            raw_text = fetch_url(url)
            if raw_text is None:
                ERR(f"Download failed — skipping {name}")
                fail_count += 1
                continue
            save_raw(name, lang, raw_text)
            INFO(f"Downloaded {len(raw_text):,} chars")
            time.sleep(1.2)  # polite crawl delay

        # ── Clean ─────────────────────────────────────────────────────────────
        if url.endswith(".htm") or url.endswith(".html") or "<html" in raw_text[:500].lower():
            cleaned = strip_html(raw_text)
        else:
            cleaned = strip_gutenberg(raw_text)

        # ── Segment (paragraph-sized: 30–200 words, not single sentences) ─────
        segments = split_into_segments(cleaned, min_words=30, max_words=200)
        segments = [s for s in segments if not is_noise(s)]

        if not segments:
            WARN(f"No usable segments from {name}")
            fail_count += 1
            continue

        # ── Save clean JSONL ──────────────────────────────────────────────────
        records = [
            {"text": seg, "lang": lang, "source": source_tag, "file": name}
            for seg in segments
        ]
        with clean_path.open("w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        if source_tag not in all_records:
            all_records[source_tag] = []
        all_records[source_tag].extend(records)

        OK(f"{len(segments):,} segments  →  {clean_path.name}")
        success_count += 1

    print()
    OK(f"Downloaded: {success_count}  |  Failed: {fail_count}  |  "
       f"Sources: {len(all_records)}")
    return all_records

# ─── STEP 3: Build master corpus ──────────────────────────────────────────────

def build_master_corpus(
    all_records: Dict[str, List[Dict]],
    max_texts: Optional[int] = None,
) -> List[str]:
    """
    Merge all records, deduplicate, shuffle, save master JSONL.
    Returns list of text strings for training.
    """
    HEAD("STEP 3 — BUILDING MASTER CORPUS")

    # Merge everything
    all_recs: List[Dict] = []
    for source_tag, recs in all_records.items():
        all_recs.extend(recs)

    # If all_records is empty (--only-train mode), load from existing JSONL files
    if not all_recs and CLEAN_DIR.exists():
        INFO("Loading from existing clean JSONL files...")
        for jf in sorted(CLEAN_DIR.glob("*.jsonl")):
            with jf.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            all_recs.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass

    if not all_recs:
        ERR("No records found. Run without --only-train first.")
        sys.exit(1)

    # Deduplicate by text (first 120 chars lowercased)
    seen: Set[str] = set()
    deduped: List[Dict] = []
    for rec in all_recs:
        key = rec["text"].strip().lower()[:120]
        if key not in seen:
            seen.add(key)
            deduped.append(rec)

    # Deterministic shuffle (reproducible)
    import random as _rng
    _rng.seed(42)
    _rng.shuffle(deduped)

    # Cap
    if max_texts and len(deduped) > max_texts:
        deduped = deduped[:max_texts]
        INFO(f"Capped to {max_texts:,} texts")

    # Save master JSONL
    with CORPUS_FILE.open("w", encoding="utf-8") as f:
        for rec in deduped:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Stats
    lang_counts: Dict[str, int] = {}
    src_counts:  Dict[str, int] = {}
    total_words = 0
    for rec in deduped:
        lang_counts[rec.get("lang", "?")] = lang_counts.get(rec.get("lang", "?"), 0) + 1
        src_counts[rec.get("source", "?")] = src_counts.get(rec.get("source", "?"), 0) + 1
        total_words += len(rec["text"].split())

    print(f"\n  ┌─ Master corpus: {len(deduped):,} texts  ({total_words:,} words)")
    print(f"  │")
    print(f"  │  Languages:")
    for lang, cnt in sorted(lang_counts.items(), key=lambda x: -x[1]):
        print(f"  │    {lang:10s}  {cnt:>6,}")
    print(f"  │")
    print(f"  │  Sources:")
    for src, cnt in sorted(src_counts.items(), key=lambda x: -x[1])[:20]:
        print(f"  │    {src:30s}  {cnt:>6,}")
    print(f"  └─ Saved → {CORPUS_FILE}")

    return [rec["text"] for rec in deduped]

# ─── STEP 4: Train ────────────────────────────────────────────────────────────

def find_santek_model() -> Optional[Path]:
    """Find santek_base_model.py by walking up from current dir."""
    candidates = [
        HERE / "santek_base_model.py",
        HERE.parent / "santek_base_model.py",
        REPO_ROOT / "santek_base_model.py",
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()
    for root in [Path.cwd(), Path.cwd().parent]:
        p = root / "santek_base_model.py"
        if p.exists():
            return p.resolve()
    return None


def run_training(
    texts:     List[str],
    epochs:    int   = 200,
    eta:       float = 0.10,
    decay:     float = 0.05,
    max_texts: Optional[int] = None,
    model_path: Optional[Path] = None,
) -> None:
    """Load santek_base_model.py dynamically and run cmd_train."""
    HEAD("STEP 4 — TRAINING SanTEK BASE MODEL")

    santek_path = find_santek_model()
    if santek_path is None:
        ERR(
            "Cannot find santek_base_model.py.\n"
            "  Place this script in the same folder as santek_base_model.py\n"
            "  or in a sub-folder (e.g. docs/) of the repo root."
        )
        sys.exit(1)

    INFO(f"Model script: {santek_path}")

    if max_texts and len(texts) > max_texts:
        INFO(f"Using first {max_texts:,} of {len(texts):,} texts")
        texts = texts[:max_texts]

    INFO(f"Texts: {len(texts):,}  |  Epochs: {epochs}  |  Eta: {eta}  |  Decay: {decay}")

    spec = importlib.util.spec_from_file_location("santek_base_model", str(santek_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules["santek_base_model"] = module
    spec.loader.exec_module(module)

    _model_path = model_path or module.DEFAULT_MODEL_PATH

    print()
    module.cmd_train(
        corpus=texts,
        epochs=epochs,
        eta=eta,
        decay=decay,
        max_streak=3,
        tension_threshold=0.10,
        patience=5,
        model_path=_model_path,
        verbose=True,
    )

    print()
    OK(f"Model saved → {_model_path}")
    print()
    INFO("To generate text from the trained model:")
    print('    python santek_base_model.py generate "OM Namah Shivaya"')
    print('    python santek_base_model.py chat')
    print('    python santek_base_model.py info')

# ─── Load from existing JSONL (no download needed) ────────────────────────────

def load_existing_corpus(max_texts: Optional[int] = None) -> List[str]:
    """Load texts from data/hindu_corpus_real.jsonl if it exists."""
    if not CORPUS_FILE.exists():
        ERR(f"No corpus file found at {CORPUS_FILE}")
        ERR("Run without --only-train first to download and build the corpus.")
        sys.exit(1)

    texts = []
    with CORPUS_FILE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rec = json.loads(line)
                    texts.append(rec["text"])
                except (json.JSONDecodeError, KeyError):
                    pass

    if max_texts and len(texts) > max_texts:
        texts = texts[:max_texts]

    INFO(f"Loaded {len(texts):,} texts from existing corpus")
    return texts

# ─── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    ap = argparse.ArgumentParser(
        description="Hindu Corpus Downloader + SanTEK Training Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Recommended: rebuild corpus (paragraphs 30-200 words), then train
  python build_hindu_corpus.py --download-only
  python build_hindu_corpus.py --check-corpus
  python build_hindu_corpus.py --skip-download --epochs 2500

  # Full pipeline (download + clean + build + train):
  python build_hindu_corpus.py

  # Download and build corpus only (no training):
  python build_hindu_corpus.py --no-train

  # Train only on existing corpus:
  python build_hindu_corpus.py --only-train --epochs 500

  # Quick test run:
  python build_hindu_corpus.py --max-texts 100 --epochs 20

  # Force re-download (ignore cached files):
  python build_hindu_corpus.py --force-download
        """,
    )
    ap.add_argument("--no-train", action="store_true",
                    help="Download and build corpus but skip training")
    ap.add_argument("--only-train", action="store_true",
                    help="Skip download; train on existing data/hindu_corpus_real.jsonl")
    ap.add_argument("--download-only", action="store_true",
                    help="Same as --no-train: download + build corpus only, do not train")
    ap.add_argument("--skip-download", action="store_true",
                    help="Same as --only-train: skip download, train on existing data/hindu_corpus_real.jsonl")
    ap.add_argument("--force-download", action="store_true",
                    help="Re-download all files even if cached")
    ap.add_argument("--epochs", type=int, default=200, help="Training epochs (default: 200)")
    ap.add_argument("--eta", type=float, default=0.10, help="Learning rate eta (default: 0.10)")
    ap.add_argument("--decay", type=float, default=0.05, help="Score decay per epoch (default: 0.05)")
    ap.add_argument("--max-texts", type=int, default=None, metavar="N",
                    help="Cap corpus at N texts (useful for testing)")
    ap.add_argument("--model", type=Path, default=None, metavar="PATH",
                    help="Output model path (default: output/santek_base_model.json)")
    ap.add_argument("--check-corpus", action="store_true",
                    help="Print corpus stats (texts, avg words) from data/hindu_corpus_real.jsonl; UTF-8 safe on Windows")
    return ap.parse_args()

# ─── Entry point ──────────────────────────────────────────────────────────────

def check_corpus_stats() -> None:
    """Print corpus stats (UTF-8 safe for Windows)."""
    if not CORPUS_FILE.exists():
        ERR(f"Corpus not found: {CORPUS_FILE}")
        sys.exit(1)
    texts = []
    with CORPUS_FILE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rec = json.loads(line)
                    texts.append(rec["text"])
                except (json.JSONDecodeError, KeyError):
                    pass
    if not texts:
        WARN("Corpus is empty.")
        return
    n, total_words = len(texts), sum(len(t.split()) for t in texts)
    avg = total_words / n
    print(f"  {n:,} texts  |  {total_words:,} words  |  avg {avg:.0f} words/text")
    print(f"  Sample: {texts[0][:120]}{'...' if len(texts[0]) > 120 else ''}")


def main():
    args = parse_args()
    # Alias flags so your exact commands work
    if getattr(args, "skip_download", False):
        args.only_train = True
    if getattr(args, "download_only", False):
        args.no_train = True

    if getattr(args, "check_corpus", False):
        check_corpus_stats()
        return

    print()
    print(_c("1;35",
        "╔══════════════════════════════════════════════════════════════╗\n"
        "║   THRESHOLD_ONSET — Hindu Corpus + SanTEK Training Pipeline ║\n"
        "║   Author: Chavala Santosh                                    ║\n"
        "╚══════════════════════════════════════════════════════════════╝"
    ))
    print(f"\n  Data directory : {DATA_DIR}")
    print(f"  Sources        : {len(SOURCES)} Hindu sacred text sources")
    print(f"  Languages      : Sanskrit · English · Telugu · Hindi · Tamil")
    print(f"  Epochs         : {args.epochs}")
    print(f"  Max texts      : {args.max_texts or 'unlimited'}")

    if args.only_train:
        texts = load_existing_corpus(max_texts=args.max_texts)
        if not args.no_train:
            run_training(
                texts=texts,
                epochs=args.epochs,
                eta=args.eta,
                decay=args.decay,
                max_texts=args.max_texts,
                model_path=args.model,
            )
        return

    all_records = download_and_clean_all(
        sources=SOURCES,
        skip_existing=not args.force_download,
    )

    texts = build_master_corpus(all_records, max_texts=args.max_texts)

    if not args.no_train and texts:
        run_training(
            texts=texts,
            epochs=args.epochs,
            eta=args.eta,
            decay=args.decay,
            max_texts=args.max_texts,
            model_path=args.model,
        )
    elif args.no_train:
        print()
        OK(f"Corpus built: {len(texts):,} texts → {CORPUS_FILE}")
        INFO("To train, run:")
        print(f"    python build_hindu_corpus.py --only-train --epochs 200")


if __name__ == "__main__":
    main()
