"""
Opt-in heavy test: SanTEK final JSON includes meta.phase10_training_summary.

Run (from repo root):
  RUN_SANTEK_PHASE10_META_TEST=1 python -m pytest tests/test_santek_phase10_meta_optional.py -m slow -v
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.mark.slow
def test_santek_phase10_training_summary_in_final_meta(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    if os.environ.get("RUN_SANTEK_PHASE10_META_TEST") != "1":
        pytest.skip("Set RUN_SANTEK_PHASE10_META_TEST=1 to run this heavy integration test.")

    monkeypatch.setenv("SANTEK_PHASE10_TRAINING_SUMMARY", "1")
    monkeypatch.setenv("SANTEK_TEXT_WORKERS", "1")
    monkeypatch.setenv("SANTEK_METHOD_WORKERS", "1")
    monkeypatch.setenv("SANTEK_DISABLE_CHECKPOINT", "1")

    from integration.model.santek_base import santek_train

    out_path = tmp_path / "santek_test_model.json"
    corpus = [
        "Action before knowledge. Function stabilizes before meaning appears.",
    ]
    santek_train(
        corpus=corpus,
        epochs=1,
        eta=0.1,
        decay=0.05,
        max_streak=3,
        tension_threshold=0.01,
        patience=99,
        verbose=False,
        methods=["word"],
        model_path=out_path,
    )

    assert out_path.is_file()
    data = json.loads(out_path.read_text(encoding="utf-8"))
    meta = data.get("meta") or {}
    p10 = meta.get("phase10_training_summary")
    assert isinstance(p10, dict), f"expected phase10_training_summary dict, got {p10!r}"
    assert int(p10.get("texts_observed", 0)) >= 1
    assert "total_directed_transitions" in p10


def test_santek_phase10_training_summary_schema_smoke(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Always-on lightweight contract check for phase10 training summary schema."""
    monkeypatch.setenv("SANTEK_PHASE10_TRAINING_SUMMARY", "1")
    monkeypatch.setenv("SANTEK_TEXT_WORKERS", "1")
    monkeypatch.setenv("SANTEK_METHOD_WORKERS", "1")
    monkeypatch.setenv("SANTEK_DISABLE_CHECKPOINT", "1")

    from integration.model.santek_base import santek_train

    out_path = tmp_path / "santek_smoke_model.json"
    santek_train(
        corpus=["Action before knowledge."],
        epochs=1,
        eta=0.1,
        decay=0.05,
        max_streak=2,
        tension_threshold=0.01,
        patience=10,
        verbose=False,
        methods=["word"],
        model_path=out_path,
    )

    data = json.loads(out_path.read_text(encoding="utf-8"))
    meta = data.get("meta")
    assert isinstance(meta, dict), "expected top-level meta object"
    p10 = meta.get("phase10_training_summary")
    assert isinstance(p10, dict), "phase10_training_summary missing from meta"
    assert isinstance(p10.get("texts_observed"), int)
    assert isinstance(p10.get("total_directed_transitions"), int)
