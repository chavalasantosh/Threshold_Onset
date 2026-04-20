"""
Phase 10 — Directed continuation layer (enterprise metrics).

Sits after structural Phases 0–4: consumes **ordered identity streams** and emits
directed successor statistics, empirical **exclusion** (never-seen successors
within the observed identity universe), and **necessity** (strict dominant
successor mass).

This is distinct from semantic discovery Phases 5–9 under ``threshold_onset.semantic``.
"""

from __future__ import annotations

from threshold_onset.phase10.analysis import dominant_successor, necessity_by_source, excluded_successors
from threshold_onset.phase10.constants import (
    DEFAULT_NECESSITY_MASS_THRESHOLD,
    MIN_TRANSITIONS_FOR_GATE,
    PAIR_KEY_SEP,
)
from threshold_onset.phase10.directed import (
    build_directed_counts,
    marginal_incoming,
    marginal_outgoing,
    phase3_undirected_edge_lookup,
    universe_from_pair_counts,
)
from threshold_onset.phase10.engine import (
    phase10_jsonable_from_model_state,
    run_phase10,
    run_phase10_from_method_states,
    run_phase10_from_model_state,
)
from threshold_onset.phase10.merge import identity_streams_from_method_states, union_phase3_metrics_for_phase10
from threshold_onset.phase10.extract import identity_sequences_from_model_state, identity_sequence_from_residue_run
from threshold_onset.phase10.types import Phase10Result, pair_key, parse_pair_key

__all__ = [
    "DEFAULT_NECESSITY_MASS_THRESHOLD",
    "MIN_TRANSITIONS_FOR_GATE",
    "PAIR_KEY_SEP",
    "Phase10Result",
    "build_directed_counts",
    "dominant_successor",
    "excluded_successors",
    "identity_sequence_from_residue_run",
    "identity_sequences_from_model_state",
    "identity_streams_from_method_states",
    "marginal_incoming",
    "marginal_outgoing",
    "necessity_by_source",
    "pair_key",
    "parse_pair_key",
    "phase10_jsonable_from_model_state",
    "phase3_undirected_edge_lookup",
    "run_phase10",
    "run_phase10_from_method_states",
    "run_phase10_from_model_state",
    "union_phase3_metrics_for_phase10",
    "universe_from_pair_counts",
]
