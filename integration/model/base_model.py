"""
Base model: save/load path_scores for reuse.

First base model = output/base_model.json created by create_base_model.py.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from integration.model.contract import PathScores

VERSION = 1
DEFAULT_PATH = Path("output/base_model.json")


def _serialize_path_scores(scores: PathScores) -> List[List[Any]]:
    """PathScores (tuple keys) -> JSON-serializable list of [from, to, score]."""
    out: List[List[Any]] = []
    for k, v in scores.items():
        if not isinstance(k, (list, tuple)) or len(k) != 2:
            continue
        a, b = k[0], k[1]
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and isinstance(v, (int, float)):
            out.append([a, b, float(v)])
    return out


def _deserialize_path_scores(data: List[List[Any]]) -> PathScores:
    """List of [from, to, score] -> PathScores."""
    scores: PathScores = {}
    for row in data:
        if len(row) >= 3:
            a, b, v = row[0], row[1], float(row[2])
            scores[(a, b)] = v
    return scores


def save_base_model(
    path_scores: PathScores,
    path: Path | str | None = None,
    *,
    learning_rate: float = 0.1,
    prediction_method: str = "highest_score",
    source: str = "create_base_model",
) -> Path:
    """Write path_scores and metadata to JSON. Returns path written."""
    from datetime import datetime, timezone
    out_path = Path(path) if path is not None else DEFAULT_PATH
    out_path = out_path.resolve()
    payload = {
        "version": VERSION,
        "path_scores": _serialize_path_scores(path_scores),
        "learning_rate": learning_rate,
        "prediction_method": prediction_method,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": source,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return out_path


def load_base_model(path: Path | str | None = None) -> Tuple[PathScores, Dict[str, Any]]:
    """Load path_scores and metadata from JSON. Returns (path_scores, metadata)."""
    in_path = Path(path) if path is not None else DEFAULT_PATH
    in_path = in_path.resolve()
    if not in_path.exists():
        raise FileNotFoundError(f"Base model not found: {in_path}")
    with open(in_path, encoding="utf-8") as f:
        payload = json.load(f)
    data = payload.get("path_scores", [])
    scores = _deserialize_path_scores(data)
    meta = {k: v for k, v in payload.items() if k != "path_scores"}
    return scores, meta
