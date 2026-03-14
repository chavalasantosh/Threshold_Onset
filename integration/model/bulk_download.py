"""
bulk_download.py — Massive corpus downloader for SanTEK / THRESHOLD_ONSET
============================================================================
Author: for Chavala Santosh

Downloads tens of millions of texts across:
  - Sanskrit, Telugu, Hindi, Tamil, English
  - Hindu sacred texts, philosophy, literature
  - Wikipedia dumps, AI4Bharat, Hugging Face, Sacred Texts, GRETIL

Target: 50M+ texts in data/bulk/ as JSONL shards
Each shard = 100,000 records (manageable file size)

Usage:
  # Install deps first (one time):
  pip install datasets requests tqdm

  # Download everything (will take hours, ~50GB+):
  python integration/model/bulk_download.py --all

  # Download specific sources:
  python integration/model/bulk_download.py --wikipedia --languages te hi ta sa
  python integration/model/bulk_download.py --ai4bharat --languages te hi ta sa
  python integration/model/bulk_download.py --sacred-texts
  python integration/model/bulk_download.py --itihasa
  python integration/model/bulk_download.py --gutenberg-sacred

  # Check what you have:
  python integration/model/bulk_download.py --status

  # Merge all shards into one corpus:
  python integration/model/bulk_download.py --merge --output data/hindu_corpus_mega.jsonl
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

BULK_DIR = Path("data/bulk")
SHARD_SIZE = 1000_000          # records per shard file
MIN_TEXT_LEN = 300             # skip texts shorter than this
MAX_TEXT_LEN = 100_000         # truncate texts longer than this
CHECKPOINT_PATH = BULK_DIR / "_download_checkpoint.json"

LANG_CODES = {
    "tel": "Telugu",
    "hin": "Hindi",
    "tam": "Tamil",
    "san": "Sanskrit",
    "eng": "English",
}


def _lang_workers() -> int:
    try:
        return max(1, int(os.environ.get("BULK_LANG_WORKERS", "2")))
    except ValueError:
        return 2


def _load_checkpoint() -> dict:
    if not CHECKPOINT_PATH.exists():
        return {}
    try:
        return json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_checkpoint(data: dict) -> None:
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _is_completed(source: str) -> bool:
    ck = _load_checkpoint()
    return bool(ck.get(source, {}).get("completed"))


def _mark_completed(source: str, total_written: int) -> None:
    ck = _load_checkpoint()
    ck[source] = {
        "completed": True,
        "records": int(total_written),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_checkpoint(ck)


def _agent_log(run_id: str, hypothesis_id: str, location: str, message: str, data: dict) -> None:
    entry = {
        "sessionId": "9f730d",
        "id": f"log_{time.time_ns()}",
        "timestamp": int(time.time() * 1000),
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
    }
    with open("debug-9f730d.log", "a", encoding="utf-8") as logf:
        logf.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _disk_state(path: Path) -> dict:
    usage = shutil.disk_usage(path)
    return {
        "free_gb": round(usage.free / (1024 ** 3), 2),
        "used_gb": round(usage.used / (1024 ** 3), 2),
        "total_gb": round(usage.total / (1024 ** 3), 2),
    }


def _is_disk_full_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return (
        "not enough space on the disk" in msg
        or "os error 112" in msg
        or "no space left on device" in msg
    )

# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def _make_id(source: str, index: int, text: str) -> str:
    h = hashlib.md5(text[:100].encode("utf-8", errors="replace")).hexdigest()[:8]
    return f"{source}_{index:08d}_{h}"


def _clean(text: str) -> str:
    """Basic text cleaning."""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _shard_path(source: str, shard_idx: int) -> Path:
    return BULK_DIR / source / f"shard_{shard_idx:05d}.jsonl"


class ShardWriter:
    """Writes records into fixed-size shards."""

    def __init__(self, source: str, shard_size: int = SHARD_SIZE):
        self.source = source
        self.shard_size = shard_size
        self.shard_idx = 0
        self.buffer: List[dict] = []
        self.total_written = 0
        self._dir = BULK_DIR / source
        self._dir.mkdir(parents=True, exist_ok=True)

    def write(self, record: dict) -> None:
        self.buffer.append(record)
        if len(self.buffer) >= self.shard_size:
            self._flush()

    def _flush(self) -> None:
        if not self.buffer:
            return
        path = _shard_path(self.source, self.shard_idx)
        with open(path, "w", encoding="utf-8") as f:
            for rec in self.buffer:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self.total_written += len(self.buffer)
        print(f"    ✓ Shard {self.shard_idx:05d} → {path.name}  ({len(self.buffer):,} records, total={self.total_written:,})")
        self.shard_idx += 1
        self.buffer = []

    def close(self) -> int:
        self._flush()
        return self.total_written


def _already_downloaded(source: str) -> int:
    """Count records already downloaded for a source."""
    d = BULK_DIR / source
    if not d.exists():
        return 0
    total = 0
    for f in d.glob("shard_*.jsonl"):
        total += sum(1 for _ in open(f, encoding="utf-8"))
    return total


# ─────────────────────────────────────────────────────────────────────────────
# Source 1: Wikipedia dumps (te, hi, ta, sa)
# ─────────────────────────────────────────────────────────────────────────────

def download_wikipedia(languages: List[str] = None) -> None:
    """Download Wikipedia via Hugging Face datasets."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("  [ERROR] pip install datasets")
        return

    if languages is None:
        languages = ["te", "hi", "ta", "sa", "en"]

    def _download_one(lang: str) -> None:
        source = f"wikipedia_{lang}"
        if _is_completed(source):
            print(f"  [SKIP] {source} already marked complete in checkpoint")
            return
        existing = _already_downloaded(source)
        if existing > 0:
            print(f"  [SKIP] {source} already has {existing:,} records")
            _mark_completed(source, existing)
            return

        print(f"\n  Downloading Wikipedia ({lang} — {LANG_CODES.get(lang, lang)})...")
        try:
            ds = load_dataset(
                "wikimedia/wikipedia",
                f"20231101.{lang}",
                split="train",
                trust_remote_code=True,
            )
            writer = ShardWriter(source)
            for i, row in enumerate(ds):
                text = _clean(str(row.get("text", "")))
                if len(text) < MIN_TEXT_LEN:
                    continue
                paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) >= MIN_TEXT_LEN]
                if not paragraphs:
                    paragraphs = [text[:MAX_TEXT_LEN]]
                for j, para in enumerate(paragraphs):
                    writer.write({
                        "id": _make_id(source, i * 100 + j, para),
                        "text": para[:MAX_TEXT_LEN],
                        "lang": lang,
                        "domain": "wikipedia",
                        "title": str(row.get("title", "")),
                    })
                if i % 10000 == 0 and i > 0:
                    print(f"    Articles processed: {i:,}")
            total = writer.close()
            _mark_completed(source, total)
            print(f"  ✓ Wikipedia {lang}: {total:,} records")
        except Exception as e:
            print(f"  [ERROR] Wikipedia {lang}: {e}")

    workers = min(_lang_workers(), len(languages))
    if workers <= 1:
        for lang in languages:
            _download_one(lang)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            list(pool.map(_download_one, languages))


# ─────────────────────────────────────────────────────────────────────────────
# Source 2: AI4Bharat Sangraha (verified Indic text)
# ─────────────────────────────────────────────────────────────────────────────

def download_ai4bharat(languages: List[str] = None) -> None:
    """Download AI4Bharat Sangraha — best quality Indic corpus."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("  [ERROR] pip install datasets")
        return

    if languages is None:
        languages = ["te", "hi", "ta", "sa"]

    for lang in languages:
        lang_3 = {"te": "tel", "hi": "hin", "ta": "tam", "sa": "san", "en": "eng"}.get(lang, lang)
        source = f"ai4bharat_{lang_3}"
        if _is_completed(source):
            print(f"  [SKIP] {source} already marked complete in checkpoint")
            continue
        existing = _already_downloaded(source)
        if existing > 0:
            print(f"  [SKIP] {source} already has {existing:,} records")
            _mark_completed(source, existing)
            continue

        print(f"\n  Downloading AI4Bharat Sangraha ({lang} -> {lang_3})...")
        # region agent log
        _agent_log(
            run_id=f"ai4bharat:{lang_3}",
            hypothesis_id="H6",
            location="integration/model/bulk_download.py:download_ai4bharat:disk_precheck",
            message="Disk state before AI4Bharat load",
            data=_disk_state(BULK_DIR),
        )
        # endregion
        try:
            # region agent log
            _agent_log(
                run_id=f"ai4bharat:{lang_3}",
                hypothesis_id="H1",
                location="integration/model/bulk_download.py:download_ai4bharat:verified_load_dataset",
                message="Calling load_dataset verified with Parquet split contract",
                data={"lang": lang, "lang_3": lang_3, "source": source, "existing": existing},
            )
            # endregion
            ds = load_dataset(
                "ai4bharat/sangraha",
                "verified",
                split=lang_3,
            )
            # region agent log
            _agent_log(
                run_id=f"ai4bharat:{lang_3}",
                hypothesis_id="H1",
                location="integration/model/bulk_download.py:download_ai4bharat:verified_loaded",
                message="Verified dataset loaded",
                data={"lang": lang, "lang_3": lang_3, "dataset_type": type(ds).__name__},
            )
            # endregion
            writer = ShardWriter(source)
            for i, row in enumerate(ds):
                text = _clean(str(row.get("text", "")))
                if len(text) < MIN_TEXT_LEN:
                    continue
                writer.write({
                    "id": _make_id(source, i, text),
                    "text": text[:MAX_TEXT_LEN],
                    "lang": lang[:2],
                    "domain": "ai4bharat_sangraha",
                })
                if i % 100000 == 0 and i > 0:
                    print(f"    Records processed: {i:,}")
            total = writer.close()
            _mark_completed(source, total)
            print(f"  ✓ AI4Bharat {lang_3}: {total:,} records")
        except Exception as e:
            # region agent log
            _agent_log(
                run_id=f"ai4bharat:{lang_3}",
                hypothesis_id="H1",
                location="integration/model/bulk_download.py:download_ai4bharat:verified_error",
                message="Verified dataset load failed",
                data={"lang": lang, "lang_3": lang_3, "error_type": type(e).__name__, "error": str(e)[:300]},
            )
            # endregion
            print(f"  [ERROR] AI4Bharat {lang_3}: {e}")
            if _is_disk_full_error(e):
                disk = _disk_state(BULK_DIR)
                print(
                    "  [ERROR] Disk is full during AI4Bharat download. "
                    f"Free space: {disk['free_gb']:.2f} GB"
                )
                print("  Free disk space, then rerun --ai4bharat.")
                continue
            print(f"  Trying unverified split...")
            try:
                # region agent log
                _agent_log(
                    run_id=f"ai4bharat:{lang_3}",
                    hypothesis_id="H2",
                    location="integration/model/bulk_download.py:download_ai4bharat:unverified_load_dataset",
                    message="Calling load_dataset unverified fallback with Parquet split contract",
                    data={"lang": lang, "lang_3": lang_3, "source": source},
                )
                # endregion
                ds = load_dataset(
                    "ai4bharat/sangraha",
                    "unverified",
                    split=lang_3,
                )
                writer = ShardWriter(source + "_unverified")
                for i, row in enumerate(ds):
                    text = _clean(str(row.get("text", "")))
                    if len(text) < MIN_TEXT_LEN:
                        continue
                    writer.write({
                        "id": _make_id(source, i, text),
                        "text": text[:MAX_TEXT_LEN],
                        "lang": lang[:2],
                        "domain": "ai4bharat_sangraha_unverified",
                    })
                total = writer.close()
                _mark_completed(source + "_unverified", total)
                print(f"  ✓ AI4Bharat {lang_3} (unverified): {total:,} records")
            except Exception as e2:
                # region agent log
                _agent_log(
                    run_id=f"ai4bharat:{lang_3}",
                    hypothesis_id="H2",
                    location="integration/model/bulk_download.py:download_ai4bharat:unverified_error",
                    message="Unverified dataset load failed",
                    data={"lang": lang, "lang_3": lang_3, "error_type": type(e2).__name__, "error": str(e2)[:300]},
                )
                # endregion
                print(f"  [ERROR] Also failed unverified: {e2}")
                if _is_disk_full_error(e2):
                    disk = _disk_state(BULK_DIR)
                    print(
                        "  [ERROR] Disk is full during unverified fallback. "
                        f"Free space: {disk['free_gb']:.2f} GB"
                    )


# ─────────────────────────────────────────────────────────────────────────────
# Source 3: Itihasa (Sanskrit-English Ramayana + Mahabharata)
# ─────────────────────────────────────────────────────────────────────────────

def download_itihasa() -> None:
    """Download Itihasa Sanskrit-English parallel corpus."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("  [ERROR] pip install datasets")
        return

    source = "itihasa"
    existing = _already_downloaded(source)
    if existing > 0:
        print(f"  [SKIP] {source} already has {existing:,} records")
        return

    print(f"\n  Downloading Itihasa (Sanskrit-English Ramayana/Mahabharata)...")
    try:
        ds = load_dataset("rahular/itihasa", split="train", trust_remote_code=True)
        writer = ShardWriter(source)
        for i, row in enumerate(ds):
            # Sanskrit
            sa_text = _clean(str(row.get("shloka", "") or row.get("sa", "")))
            en_text = _clean(str(row.get("translation", "") or row.get("en", "")))
            if sa_text and len(sa_text) >= MIN_TEXT_LEN:
                writer.write({
                    "id": _make_id(source + "_sa", i, sa_text),
                    "text": sa_text,
                    "lang": "sa",
                    "domain": "itihasa",
                })
            if en_text and len(en_text) >= MIN_TEXT_LEN:
                writer.write({
                    "id": _make_id(source + "_en", i, en_text),
                    "text": en_text,
                    "lang": "en",
                    "domain": "itihasa",
                })
        total = writer.close()
        print(f"  ✓ Itihasa: {total:,} records")
    except Exception as e:
        print(f"  [ERROR] Itihasa: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Source 4: IndicCorp (massive multilingual)
# ─────────────────────────────────────────────────────────────────────────────

def download_indicorp(languages: List[str] = None) -> None:
    """Download AI4Bharat IndicCorp v2 — billions of words."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("  [ERROR] pip install datasets")
        return

    if languages is None:
        languages = ["te", "hi", "ta", "sa"]

    lang_map = {
        "te": "Telugu",
        "hi": "Hindi",
        "ta": "Tamil",
        "sa": "Sanskrit",
    }

    for lang in languages:
        source = f"indicorp_{lang}"
        existing = _already_downloaded(source)
        if existing > 0:
            print(f"  [SKIP] {source} already has {existing:,} records")
            continue

        print(f"\n  Downloading IndicCorp v2 ({lang} — {lang_map.get(lang, lang)})...")
        try:
            ds = load_dataset(
                "ai4bharat/IndicCorp",
                lang,
                split="train",
                trust_remote_code=True,
                streaming=True,   # stream to avoid loading all into RAM
            )
            writer = ShardWriter(source)
            for i, row in enumerate(ds):
                text = _clean(str(row.get("text", "") or row.get("sentence", "")))
                if len(text) < MIN_TEXT_LEN:
                    continue
                writer.write({
                    "id": _make_id(source, i, text),
                    "text": text[:MAX_TEXT_LEN],
                    "lang": lang,
                    "domain": "indicorp",
                })
                if i % 500000 == 0 and i > 0:
                    print(f"    Records processed: {i:,}")
                # Cap at 5M per language to avoid running forever
                if i >= 5_000_000:
                    print(f"    Capped at 5M records for {lang}")
                    break
            total = writer.close()
            print(f"  ✓ IndicCorp {lang}: {total:,} records")
        except Exception as e:
            print(f"  [ERROR] IndicCorp {lang}: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Source 5: CC-100 (Common Crawl multilingual)
# ─────────────────────────────────────────────────────────────────────────────

def download_cc100(languages: List[str] = None) -> None:
    """Download CC-100 multilingual corpus."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("  [ERROR] pip install datasets")
        return

    if languages is None:
        languages = ["te", "hi", "ta"]   # sa not in CC-100

    for lang in languages:
        source = f"cc100_{lang}"
        existing = _already_downloaded(source)
        if existing > 0:
            print(f"  [SKIP] {source} already has {existing:,} records")
            continue

        print(f"\n  Downloading CC-100 ({lang})...")
        try:
            ds = load_dataset(
                "cc100",
                lang=lang,
                split="train",
                trust_remote_code=True,
                streaming=True,
            )
            writer = ShardWriter(source)
            for i, row in enumerate(ds):
                text = _clean(str(row.get("text", "")))
                if len(text) < MIN_TEXT_LEN:
                    continue
                writer.write({
                    "id": _make_id(source, i, text),
                    "text": text[:MAX_TEXT_LEN],
                    "lang": lang,
                    "domain": "cc100",
                })
                if i % 500000 == 0 and i > 0:
                    print(f"    Records: {i:,}")
                if i >= 3_000_000:
                    print(f"    Capped at 3M for {lang}")
                    break
            total = writer.close()
            print(f"  ✓ CC-100 {lang}: {total:,} records")
        except Exception as e:
            print(f"  [ERROR] CC-100 {lang}: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Source 6: Sacred texts scraper (sacred-texts.com)
# ─────────────────────────────────────────────────────────────────────────────

SACRED_TEXT_URLS = [
    # Vedas
    ("https://www.sacred-texts.com/hin/rigveda/index.htm", "en", "rigveda"),
    ("https://www.sacred-texts.com/hin/av/index.htm", "en", "atharvaveda"),
    ("https://www.sacred-texts.com/hin/sbr/index.htm", "en", "shatapatha_brahmana"),
    # Upanishads
    ("https://www.sacred-texts.com/hin/upan/index.htm", "en", "upanishads"),
    ("https://www.sacred-texts.com/hin/chandogya.htm", "en", "chandogya"),
    # Gita
    ("https://www.sacred-texts.com/hin/gita/index.htm", "en", "bhagavad_gita"),
    # Puranas
    ("https://www.sacred-texts.com/hin/vp/index.htm", "en", "vishnu_purana"),
    ("https://www.sacred-texts.com/hin/m/index.htm", "en", "mahabharata"),
    ("https://www.sacred-texts.com/hin/rama/index.htm", "en", "ramayana"),
    # Philosophy
    ("https://www.sacred-texts.com/hin/yogasutr.htm", "en", "yoga_sutras"),
    ("https://www.sacred-texts.com/hin/laws-of-manu.htm", "en", "manu_smriti"),
]


def _fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 SanTEK-Corpus-Builder"})
        with urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def _extract_text_from_html(html: str) -> str:
    """Very basic HTML text extraction."""
    # Remove scripts and styles
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Decode entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ').replace('&#39;', "'").replace('&quot;', '"')
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _extract_links(html: str, base_url: str) -> List[str]:
    """Extract absolute links from HTML."""
    from urllib.parse import urljoin
    links = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    base = base_url.rsplit('/', 1)[0]
    result = []
    for link in links:
        if link.startswith('http'):
            result.append(link)
        elif not link.startswith('#') and not link.startswith('mailto'):
            result.append(urljoin(base_url, link))
    return result


def download_sacred_texts() -> None:
    """Scrape sacred-texts.com for Hindu texts."""
    source = "sacred_texts"
    existing = _already_downloaded(source)
    if existing > 0:
        print(f"  [SKIP] {source} already has {existing:,} records")
        return

    print(f"\n  Scraping sacred-texts.com...")
    writer = ShardWriter(source)
    visited = set()
    total_pages = 0

    for index_url, lang, domain in SACRED_TEXT_URLS:
        print(f"    Fetching index: {domain}")
        html = _fetch_url(index_url)
        if not html:
            print(f"    [SKIP] Could not fetch {index_url}")
            continue

        # Get sub-links from index page
        links = [index_url] + [
            l for l in _extract_links(html, index_url)
            if 'sacred-texts.com/hin' in l and l not in visited
        ]

        for url in links[:200]:   # cap per source
            if url in visited:
                continue
            visited.add(url)
            time.sleep(0.3)   # polite crawl delay

            page_html = _fetch_url(url)
            if not page_html:
                continue

            text = _extract_text_from_html(page_html)
            # Split into paragraphs
            paragraphs = [p.strip() for p in text.split('  ') if len(p.strip()) >= MIN_TEXT_LEN]
            for j, para in enumerate(paragraphs[:50]):
                writer.write({
                    "id": _make_id(source, total_pages * 50 + j, para),
                    "text": para[:MAX_TEXT_LEN],
                    "lang": lang,
                    "domain": domain,
                    "source_url": url,
                })
            total_pages += 1

        print(f"    ✓ {domain}: {total_pages} pages so far")

    total = writer.close()
    print(f"  ✓ Sacred texts: {total:,} records from {total_pages} pages")


# ─────────────────────────────────────────────────────────────────────────────
# Source 7: OPUS multilingual (Sanskrit + Indian languages)
# ─────────────────────────────────────────────────────────────────────────────

def download_opus(languages: List[str] = None) -> None:
    """Download OPUS multilingual corpora."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("  [ERROR] pip install datasets")
        return

    if languages is None:
        languages = ["hi", "te", "ta"]

    for lang in languages:
        source = f"opus_{lang}"
        existing = _already_downloaded(source)
        if existing > 0:
            print(f"  [SKIP] {source} already has {existing:,} records")
            continue

        print(f"\n  Downloading OPUS ({lang})...")
        try:
            ds = load_dataset(
                "Helsinki-NLP/opus-100",
                f"en-{lang}",
                split="train",
                trust_remote_code=True,
            )
            writer = ShardWriter(source)
            for i, row in enumerate(ds):
                trans = row.get("translation", {})
                for l, text in trans.items():
                    text = _clean(str(text))
                    if len(text) >= MIN_TEXT_LEN:
                        writer.write({
                            "id": _make_id(source, i * 2, text),
                            "text": text[:MAX_TEXT_LEN],
                            "lang": l if l in LANG_CODES else "en",
                            "domain": "opus",
                        })
            total = writer.close()
            print(f"  ✓ OPUS {lang}: {total:,} records")
        except Exception as e:
            print(f"  [ERROR] OPUS {lang}: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Merge all shards
# ─────────────────────────────────────────────────────────────────────────────

def merge_all(output_path: Path) -> None:
    """Merge all downloaded shards into one corpus JSONL."""
    if not BULK_DIR.exists():
        print("  No bulk data found. Run downloads first.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    seen_ids = set()
    duplicate_ids = 0
    missing_ids = 0
    decode_errors = 0

    print(f"\n  Merging all shards → {output_path}")
    # region agent log
    _agent_log(
        run_id=f"merge:{output_path.name}",
        hypothesis_id="H3",
        location="integration/model/bulk_download.py:merge_all:start",
        message="Merge started",
        data={"output_path": str(output_path)},
    )
    # endregion
    with open(output_path, "w", encoding="utf-8") as out:
        for shard_file in sorted(BULK_DIR.rglob("shard_*.jsonl")):
            file_count = 0
            with open(shard_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        rec_id = obj.get("id", "")
                        if not rec_id:
                            missing_ids += 1
                        if rec_id in seen_ids:
                            duplicate_ids += 1
                            continue
                        seen_ids.add(rec_id)
                        out.write(json.dumps(obj, ensure_ascii=False) + "\n")
                        total += 1
                        file_count += 1
                    except json.JSONDecodeError:
                        decode_errors += 1
                        continue
            print(f"    {shard_file.parent.name}/{shard_file.name}: {file_count:,} records")

    print(f"\n  ✓ Merged {total:,} total records → {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
    # region agent log
    _agent_log(
        run_id=f"merge:{output_path.name}",
        hypothesis_id="H3",
        location="integration/model/bulk_download.py:merge_all:end",
        message="Merge finished with counters",
        data={
            "total_written": total,
            "unique_ids": len(seen_ids),
            "duplicate_ids": duplicate_ids,
            "missing_ids": missing_ids,
            "decode_errors": decode_errors,
        },
    )
    # endregion


# ─────────────────────────────────────────────────────────────────────────────
# Status report
# ─────────────────────────────────────────────────────────────────────────────

def show_status() -> None:
    """Show what's been downloaded."""
    print(f"\n  {'='*55}")
    print(f"  SanTEK Corpus Status")
    print(f"  {'='*55}")

    if not BULK_DIR.exists():
        print(f"  No data yet. Run: python bulk_download.py --all")
        return

    grand_total = 0
    for source_dir in sorted(BULK_DIR.iterdir()):
        if not source_dir.is_dir():
            continue
        shards = list(source_dir.glob("shard_*.jsonl"))
        if not shards:
            continue
        count = sum(sum(1 for _ in open(f, encoding="utf-8")) for f in shards)
        size_mb = sum(f.stat().st_size for f in shards) / 1024 / 1024
        grand_total += count
        print(f"  {source_dir.name:30s}  {count:>10,} records  {size_mb:6.1f} MB  ({len(shards)} shards)")

    print(f"  {'─'*55}")
    print(f"  {'TOTAL':30s}  {grand_total:>10,} records")
    print()

    # Also check existing corpus
    existing = Path("data/hindu_corpus_real.jsonl")
    if existing.exists():
        existing_count = sum(1 for _ in open(existing, encoding="utf-8"))
        print(f"  Existing corpus: {existing_count:,} records ({existing.stat().st_size/1024/1024:.1f} MB)")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="SanTEK Bulk Corpus Downloader — tens of millions of texts"
    )
    ap.add_argument("--all", action="store_true", help="Download everything")
    ap.add_argument("--wikipedia", action="store_true")
    ap.add_argument("--ai4bharat", action="store_true")
    ap.add_argument("--indicorp", action="store_true")
    ap.add_argument("--cc100", action="store_true")
    ap.add_argument("--sacred-texts", action="store_true", dest="sacred_texts")
    ap.add_argument("--itihasa", action="store_true")
    ap.add_argument("--opus", action="store_true")
    ap.add_argument("--languages", nargs="+", default=["te", "hi", "ta", "sa"],
                    help="Language codes (default: te hi ta sa)")
    ap.add_argument("--merge", action="store_true", help="Merge all shards into one file")
    ap.add_argument("--output", type=Path, default=Path("data/hindu_corpus_mega.jsonl"))
    ap.add_argument("--status", action="store_true", help="Show download status")
    args = ap.parse_args()

    BULK_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 60)
    print("  SanTEK Bulk Corpus Downloader")
    print("  Target: tens of millions of texts")
    print("=" * 60)
    print(f"  Languages : {args.languages}")
    print(f"  Output dir: {BULK_DIR}")
    print()

    if args.status:
        show_status()
        return

    if args.merge:
        merge_all(args.output)
        return

    if args.all or args.wikipedia:
        download_wikipedia(args.languages)

    if args.all or args.ai4bharat:
        download_ai4bharat(args.languages)

    if args.all or args.itihasa:
        download_itihasa()

    if args.all or args.indicorp:
        download_indicorp(args.languages)

    if args.all or args.cc100:
        download_cc100([l for l in args.languages if l != "sa"])

    if args.all or args.opus:
        download_opus([l for l in args.languages if l != "sa"])

    if args.all or args.sacred_texts:
        download_sacred_texts()

    show_status()

    if args.all:
        print(f"\n  All downloads complete.")
        print("  Now merge:")
        print("    python integration/model/bulk_download.py --merge --output data/hindu_corpus_mega.jsonl")
        print("  Then make it the training corpus path expected by build_hindu_corpus.py:")
        print("    Copy-Item data/hindu_corpus_mega.jsonl data/hindu_corpus_real.jsonl -Force")
        print("  Then train:")
        print("    python build_hindu_corpus.py --skip-download --epochs 500")


if __name__ == "__main__":
    main()