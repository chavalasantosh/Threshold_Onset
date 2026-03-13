"""
Canonical corpus loader and deterministic train/val/test split.

Corpus format: UTF-8 JSONL, one record per line:
  {"id": "...", "text": "...", "lang": "...", "domain": "..."}  (domain optional)

Split: deterministic by stable hash, stratified by language (same lang ratio in each split).
Stdlib only. No third-party imports.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Default split ratios: train / val / test
DEFAULT_TRAIN_RATIO = 0.80
DEFAULT_VAL_RATIO = 0.10
DEFAULT_TEST_RATIO = 0.10
SPLIT_SEED = b"santek_v1_split"  # stable for reproducibility


@dataclass
class CorpusRecord:
    """One corpus sample with required id, text, lang and optional domain."""
    id: str
    text: str
    lang: str
    domain: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"id": self.id, "text": self.text, "lang": self.lang}
        if self.domain is not None:
            d["domain"] = self.domain
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CorpusRecord":
        return cls(
            id=str(d.get("id", "")),
            text=str(d.get("text", "")).strip(),
            lang=str(d.get("lang", "unknown")).strip() or "unknown",
            domain=str(d["domain"]).strip() if d.get("domain") else None,
        )


@dataclass
class SplitManifest:
    """Manifest of which record ids went to which split (reproducibility)."""
    train_ids: List[str] = field(default_factory=list)
    val_ids: List[str] = field(default_factory=list)
    test_ids: List[str] = field(default_factory=list)
    train_ratio: float = DEFAULT_TRAIN_RATIO
    val_ratio: float = DEFAULT_VAL_RATIO
    test_ratio: float = DEFAULT_TEST_RATIO
    source_path: Optional[str] = None
    total_records: int = 0
    lang_counts: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "train_ids": self.train_ids,
            "val_ids": self.val_ids,
            "test_ids": self.test_ids,
            "train_ratio": self.train_ratio,
            "val_ratio": self.val_ratio,
            "test_ratio": self.test_ratio,
            "source_path": self.source_path,
            "total_records": self.total_records,
            "lang_counts": self.lang_counts,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SplitManifest":
        return cls(
            train_ids=list(d.get("train_ids", [])),
            val_ids=list(d.get("val_ids", [])),
            test_ids=list(d.get("test_ids", [])),
            train_ratio=float(d.get("train_ratio", DEFAULT_TRAIN_RATIO)),
            val_ratio=float(d.get("val_ratio", DEFAULT_VAL_RATIO)),
            test_ratio=float(d.get("test_ratio", DEFAULT_TEST_RATIO)),
            source_path=d.get("source_path"),
            total_records=int(d.get("total_records", 0)),
            lang_counts=dict(d.get("lang_counts", {})),
        )


def _stable_hash(record_id: str, seed: bytes = SPLIT_SEED) -> int:
    """Deterministic hash in [0, 1e9) for split assignment."""
    h = hashlib.sha256(seed + record_id.encode("utf-8", errors="replace")).hexdigest()
    return int(h[:15], 16) % 1_000_000_000


def load_jsonl_corpus(path: Path) -> List[CorpusRecord]:
    """Load UTF-8 JSONL corpus; one JSON object per line. Skips blank lines and invalid lines."""
    records: List[CorpusRecord] = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                if not isinstance(d, dict):
                    continue
                rec = CorpusRecord.from_dict(d)
                if not rec.text:
                    continue
                if not rec.id:
                    rec.id = f"line_{i}"
                records.append(rec)
            except (json.JSONDecodeError, TypeError):
                continue
    return records


def split_train_val_test(
    records: List[CorpusRecord],
    train_ratio: float = DEFAULT_TRAIN_RATIO,
    val_ratio: float = DEFAULT_VAL_RATIO,
    test_ratio: float = DEFAULT_TEST_RATIO,
    seed: bytes = SPLIT_SEED,
) -> Tuple[List[CorpusRecord], List[CorpusRecord], List[CorpusRecord], SplitManifest]:
    """
    Deterministic split stratified by language.

    Within each language, records are ordered by stable hash and assigned to
    train/val/test so that each language gets roughly the same ratios.
    """
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
        raise ValueError("train_ratio + val_ratio + test_ratio must equal 1.0")

    by_lang: Dict[str, List[CorpusRecord]] = {}
    for r in records:
        by_lang.setdefault(r.lang, []).append(r)

    train_list: List[CorpusRecord] = []
    val_list: List[CorpusRecord] = []
    test_list: List[CorpusRecord] = []

    for lang, lang_records in by_lang.items():
        # Sort by stable hash for reproducibility within language
        keyed = [(_stable_hash(r.id, seed), r) for r in lang_records]
        keyed.sort(key=lambda x: x[0])
        ordered = [r for _, r in keyed]
        n = len(ordered)
        if n == 0:
            continue
        i_train = max(1, int(n * train_ratio))
        i_val = max(i_train, min(i_train + 1, int(n * (train_ratio + val_ratio))))
        train_list.extend(ordered[:i_train])
        val_list.extend(ordered[i_train:i_val])
        test_list.extend(ordered[i_val:])

    manifest = SplitManifest(
        train_ids=[r.id for r in train_list],
        val_ids=[r.id for r in val_list],
        test_ids=[r.id for r in test_list],
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
        total_records=len(records),
        lang_counts={lang: len(recs) for lang, recs in by_lang.items()},
    )
    return train_list, val_list, test_list, manifest


def load_and_split(
    path: Path,
    train_ratio: float = DEFAULT_TRAIN_RATIO,
    val_ratio: float = DEFAULT_VAL_RATIO,
    test_ratio: float = DEFAULT_TEST_RATIO,
) -> Tuple[List[CorpusRecord], List[CorpusRecord], List[CorpusRecord], SplitManifest]:
    """Load JSONL corpus and return train/val/test splits + manifest."""
    records = load_jsonl_corpus(path)
    if not records:
        return [], [], [], SplitManifest(source_path=str(path), total_records=0)
    manifest = SplitManifest(source_path=str(path))
    train, val, test, manifest = split_train_val_test(
        records, train_ratio, val_ratio, test_ratio
    )
    manifest.source_path = str(path)
    return train, val, test, manifest


def texts_from_records(records: List[CorpusRecord]) -> List[str]:
    """Extract text list for trainer (order preserved)."""
    return [r.text for r in records]
