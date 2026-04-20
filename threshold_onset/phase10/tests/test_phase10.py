"""Unit tests for Phase 10 directed continuation."""

from __future__ import annotations

import pytest

from threshold_onset.phase10 import (
    Phase10Result,
    dominant_successor,
    phase10_jsonable_from_model_state,
    run_phase10,
    run_phase10_from_method_states,
    run_phase10_from_model_state,
)
from threshold_onset.phase10.extract import identity_sequence_from_residue_run


def test_run_phase10_counts_and_gate() -> None:
    r = run_phase10([["x", "y", "x", "y"]])
    assert r.gate_passed
    assert r.total_transitions == 3
    assert r.pair_counts[("x", "y")] == 2
    assert r.pair_counts[("y", "x")] == 1
    assert set(r.universe_ids) == {"x", "y"}


def test_self_loop_counted() -> None:
    r = run_phase10([["a", "a", "a"]])
    assert r.total_transitions == 2
    assert r.pair_counts[("a", "a")] == 2


def test_gate_fails_when_no_transitions() -> None:
    r = run_phase10([["only_one"]])
    assert not r.gate_passed
    assert r.gate_reason == "insufficient_transitions"
    assert r.total_transitions == 0


def test_necessity_threshold_one() -> None:
    r = run_phase10([["a", "b", "a", "b"]], necessity_mass_threshold=1.0)
    assert r.necessity_by_source["a"] == {"successor": "b", "mass_fraction": 1.0}
    assert r.necessity_by_source["b"] == {"successor": "a", "mass_fraction": 1.0}


def test_necessity_tie_returns_none() -> None:
    r = run_phase10([["a", "b", "a", "c"]], necessity_mass_threshold=0.5)
    assert r.necessity_by_source["a"] is None


def test_excluded_within_universe() -> None:
    r = run_phase10([["a", "b"]])
    assert "c" not in r.excluded_successors  # c not in universe
    # From a only b was observed as successor; a itself never followed a.
    assert r.excluded_successors["a"] == ("a",)
    # b has no outgoing mass: every universe id is a never-seen successor.
    assert r.excluded_successors["b"] == ("a", "b")


def test_cross_check_phase3_filters() -> None:
    p3 = {"graph_edges": {("a", "b")}}
    r_all = run_phase10([["a", "b", "a", "c"]], cross_check_phase3=False)
    r_f = run_phase10([["a", "b", "a", "c"]], cross_check_phase3=True, phase3_metrics=p3)
    assert r_all.pair_counts.get(("a", "c"), 0) == 1
    assert r_f.pair_counts.get(("a", "c"), 0) == 0
    assert r_f.pair_counts[("a", "b")] == 1


def test_phase10_jsonable_prefers_embedded() -> None:
    ms = {
        "phase10_metrics": {"phase": "phase10", "gate_passed": True, "total_transitions": 99},
        "phase2_metrics": {},
        "residue_sequences": [],
    }
    j = phase10_jsonable_from_model_state(ms)
    assert j is not None
    assert j["total_transitions"] == 99


def test_json_round_trip() -> None:
    r = run_phase10([["p", "q", "p"]])
    blob = r.to_jsonable()
    r2 = Phase10Result.from_jsonable(blob)
    assert r2.pair_counts == r.pair_counts
    assert r2.universe_ids == r.universe_ids
    assert r2.excluded_successors == r.excluded_successors


def test_dominant_successor_validation() -> None:
    with pytest.raises(ValueError):
        dominant_successor({"a": 1}, mass_threshold=0.0)


def test_identity_sequence_from_residue_run() -> None:
    # Two-step run: one segment hash maps to id1
    from threshold_onset.phase10.extract import segment_hash_residue_pair

    h = segment_hash_residue_pair(1.0, 2.0)
    seq = identity_sequence_from_residue_run([1.0, 2.0], {h: "id1"})
    assert seq == ["id1"]


def test_run_phase10_from_method_states_merges_streams() -> None:
    """Two tokenizer states on same synthetic identities → combined transition counts."""
    md5 = __import__("hashlib").md5
    h12 = md5(str((1.0, 2.0)).encode("utf-8")).hexdigest()
    h23 = md5(str((2.0, 3.0)).encode("utf-8")).hexdigest()
    state1 = {
        "phase2_metrics": {"identity_mappings": {h12: "ida", h23: "idb"}},
        "residue_sequences": [[1.0, 2.0, 3.0]],
    }
    state2 = {
        "phase2_metrics": {"identity_mappings": {h12: "ida", h23: "idc"}},
        "residue_sequences": [[1.0, 2.0, 3.0]],
    }
    r = run_phase10_from_method_states([("word", state1), ("char", state2)])
    assert r.pair_counts[("ida", "idb")] == 1
    assert r.pair_counts[("ida", "idc")] == 1
    assert r.total_transitions == 2


def test_run_phase10_from_model_state() -> None:
    md5 = __import__("hashlib").md5
    h12 = md5(str((1.0, 2.0)).encode("utf-8")).hexdigest()
    h23 = md5(str((2.0, 3.0)).encode("utf-8")).hexdigest()
    state = {
        "phase2_metrics": {"identity_mappings": {h12: "ida", h23: "idb"}},
        "residue_sequences": [[1.0, 2.0, 3.0]],
    }
    r = run_phase10_from_model_state(state)
    assert r.gate_passed
    assert r.pair_counts == {("ida", "idb"): 1}
