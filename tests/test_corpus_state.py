"""Tests for CorpusState (Phase 1 corpus structural memory)."""

import json
import tempfile
from pathlib import Path

import pytest

# Add project root for imports
import sys
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from threshold_onset.corpus_state import CorpusState, _edge_key


def test_edge_key():
    """Canonical edge key is (min, max)."""
    assert _edge_key("a", "b") == ("a", "b")
    assert _edge_key("b", "a") == ("a", "b")


def test_corpus_state_reinforcement():
    """Present identities get reinforced."""
    state = CorpusState(reinforcement=1.0, decay_rate=0.1)
    state.update(identity_hashes={"h1", "h2"}, edge_pairs={("h1", "h2")})

    assert state.get_identity_stability("h1") == 1.0
    assert state.get_identity_stability("h2") == 1.0
    assert state.get_edge_weight("h1", "h2") == 1.0
    assert state.doc_count == 1


def test_corpus_state_decay():
    """Absent identities decay."""
    state = CorpusState(reinforcement=1.0, decay_rate=0.5)
    state.update(identity_hashes={"h1"}, edge_pairs=set())
    assert state.get_identity_stability("h1") == 1.0

    state.update(identity_hashes=set(), edge_pairs=set())  # h1 absent
    assert state.get_identity_stability("h1") == 0.5  # 1.0 * (1 - 0.5)


def test_corpus_state_recurrence():
    """Recurring identities grow; one-off decay."""
    state = CorpusState(reinforcement=1.0, decay_rate=0.2, prune_interval_docs=100)
    # Doc 1: h1, h2
    state.update(identity_hashes={"h1", "h2"}, edge_pairs={("h1", "h2")})
    # Doc 2: h1 only (h2 absent)
    state.update(identity_hashes={"h1"}, edge_pairs=set())
    # Doc 3: h1, h2
    state.update(identity_hashes={"h1", "h2"}, edge_pairs={("h1", "h2")})

    assert state.get_identity_stability("h1") > state.get_identity_stability("h2")
    assert "h1" in state.identity_stability
    assert "h2" in state.identity_stability


def test_corpus_state_save_load():
    """State persists to JSON and loads correctly."""
    state = CorpusState(reinforcement=1.0, decay_rate=0.1)
    state.update(identity_hashes={"a", "b"}, edge_pairs={("a", "b")})

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)
    try:
        state.save(path)
        loaded = CorpusState.load(path)
        assert loaded.identity_stability == state.identity_stability
        assert loaded.edge_weights == state.edge_weights
        assert loaded.core_identities == state.core_identities
        assert loaded.doc_count == state.doc_count
    finally:
        path.unlink(missing_ok=True)


def test_corpus_state_metrics():
    """Metrics return correct counts."""
    state = CorpusState()
    state.update(identity_hashes={"h1", "h2"}, edge_pairs={("h1", "h2")})
    m = state.metrics()
    assert m["corpus_identities_count"] == 2
    assert m["corpus_edges_count"] == 1
    assert m["corpus_doc_count"] == 1
