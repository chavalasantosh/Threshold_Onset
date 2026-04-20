"""
Phase 10 — main entry: directed continuation, exclusion, necessity.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from threshold_onset.phase10.analysis import build_marginals, excluded_successors, necessity_by_source
from threshold_onset.phase10.constants import DEFAULT_NECESSITY_MASS_THRESHOLD, MIN_TRANSITIONS_FOR_GATE
from threshold_onset.phase10.directed import build_directed_counts, universe_from_pair_counts
from threshold_onset.phase10.types import Phase10Result


def run_phase10(
    identity_sequences: Sequence[Sequence[str]],
    *,
    cross_check_phase3: bool = False,
    phase3_metrics: Optional[Dict[str, Any]] = None,
    necessity_mass_threshold: float = DEFAULT_NECESSITY_MASS_THRESHOLD,
    min_transitions_gate: int = MIN_TRANSITIONS_FOR_GATE,
) -> Phase10Result:
    """
    Build Phase 10 metrics from ordered identity streams (one list per run/epoch).

    Does not mutate Phase 0–4 outputs; consumes sequences only.

    Args:
        identity_sequences: Each inner sequence is time-ordered identity hashes.
        cross_check_phase3: If True, drop transitions not licensed by Phase 3 edges.
        phase3_metrics: Phase 3 metrics dict (expects ``graph_edges``).
        necessity_mass_threshold: Min mass on strict max-successor for necessity (0, 1].
        min_transitions_gate: Minimum total directed transitions to pass the gate.
    """
    if min_transitions_gate < 0:
        raise ValueError("min_transitions_gate must be non-negative")
    if necessity_mass_threshold <= 0.0 or necessity_mass_threshold > 1.0:
        raise ValueError("necessity_mass_threshold must be in (0, 1]")

    pair_counts, total = build_directed_counts(
        identity_sequences,
        cross_check_phase3=cross_check_phase3,
        phase3_metrics=phase3_metrics,
    )
    outgoing, incoming = build_marginals(pair_counts)
    universe = universe_from_pair_counts(pair_counts)
    excl = excluded_successors(universe, outgoing)
    nec = necessity_by_source(outgoing, necessity_mass_threshold)

    gate_passed = total >= min_transitions_gate
    gate_reason = "ok" if gate_passed else "insufficient_transitions"

    return Phase10Result(
        gate_passed=gate_passed,
        gate_reason=gate_reason,
        total_transitions=total,
        cross_check_phase3=cross_check_phase3,
        necessity_mass_threshold=necessity_mass_threshold,
        pair_counts=pair_counts,
        outgoing=outgoing,
        incoming=incoming,
        universe_ids=tuple(universe),
        necessity_by_source=nec,
        excluded_successors={k: tuple(v) for k, v in sorted(excl.items())},
    )


def run_phase10_from_model_state(
    model_state: Dict[str, Any],
    *,
    cross_check_phase3: bool = False,
    necessity_mass_threshold: float = DEFAULT_NECESSITY_MASS_THRESHOLD,
    min_transitions_gate: int = MIN_TRANSITIONS_FOR_GATE,
) -> Phase10Result:
    """
    Convenience: extract identity streams from ``model_state`` and run Phase 10.

    Expects ``phase2_metrics.identity_mappings`` and ``residue_sequences`` like
    the integration pipeline.
    """
    from threshold_onset.phase10.extract import identity_sequences_from_model_state

    streams = identity_sequences_from_model_state(model_state)
    p3 = model_state.get("phase3_metrics") if cross_check_phase3 else None
    return run_phase10(
        streams,
        cross_check_phase3=cross_check_phase3,
        phase3_metrics=p3 if isinstance(p3, dict) else None,
        necessity_mass_threshold=necessity_mass_threshold,
        min_transitions_gate=min_transitions_gate,
    )


def phase10_jsonable_from_model_state(
    model_state: Mapping[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Snapshot for downstream consumers (e.g. semantic Phase 5 metadata).

    Uses embedded ``model_state["phase10_metrics"]`` when present and valid;
    otherwise computes via ``run_phase10_from_model_state``. Returns None if
    computation fails.
    """
    embedded = model_state.get("phase10_metrics")
    if isinstance(embedded, dict) and embedded.get("phase") == "phase10":
        return dict(embedded)
    try:
        return run_phase10_from_model_state(dict(model_state)).to_jsonable()
    except Exception:
        return None


def run_phase10_from_method_states(
    method_states: Sequence[Tuple[Any, Mapping[str, Any]]],
    *,
    cross_check_phase3: bool = False,
    necessity_mass_threshold: float = DEFAULT_NECESSITY_MASS_THRESHOLD,
    min_transitions_gate: int = MIN_TRANSITIONS_FOR_GATE,
) -> Phase10Result:
    """
    Phase 10 over **all** tokenizer views of the same text (SanTEK-style list).

    Concatenates identity streams from each ``(method_name, model_state)`` pair.
    When ``cross_check_phase3`` is True, unions ``graph_edges`` from every
    ``model_state["phase3_metrics"]`` before filtering transitions.
    """
    from threshold_onset.phase10.merge import (
        identity_streams_from_method_states,
        union_phase3_metrics_for_phase10,
    )

    streams = identity_streams_from_method_states(method_states)
    p3: Optional[Dict[str, Any]] = None
    if cross_check_phase3:
        p3 = union_phase3_metrics_for_phase10(method_states)
    return run_phase10(
        streams,
        cross_check_phase3=cross_check_phase3,
        phase3_metrics=p3,
        necessity_mass_threshold=necessity_mass_threshold,
        min_transitions_gate=min_transitions_gate,
    )
