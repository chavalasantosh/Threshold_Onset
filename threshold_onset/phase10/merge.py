"""
Phase 10 — combine identity streams from multiple pipeline model_state dicts.

Used when the same text is run under several tokenization methods (e.g. SanTEK
training): each method yields its own residue → identity streams. Concatenating
those streams produces an empirical directed index over **all** structural
views. Identity strings are method-specific hashes; the union universe may
contain labels that are numerically equal across methods only by hash collision
(extremely unlikely with MD5 hex).
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence, Set, Tuple

from threshold_onset.phase10.extract import identity_sequences_from_model_state

MethodState = Tuple[Any, Mapping[str, Any]]


def identity_streams_from_method_states(
    method_states: Sequence[MethodState],
) -> List[List[str]]:
    """
    Flatten ``identity_sequences_from_model_state`` across all method states.

    Order: methods appear in sequence order; within each state, runs keep
    pipeline order.
    """
    out: List[List[str]] = []
    for _method_name, ms in method_states:
        out.extend(identity_sequences_from_model_state(ms))
    return out


def union_phase3_metrics_for_phase10(
    method_states: Sequence[MethodState],
) -> Dict[str, Any]:
    """
    Merge Phase 3 ``graph_edges`` from every model_state into one metrics dict.

    ``directed.phase3_undirected_edge_lookup`` expands each undirected edge into
    both orientations for transition filtering.
    """
    edges: Set[Tuple[str, str]] = set()
    for _method_name, ms in method_states:
        p3 = ms.get("phase3_metrics") or {}
        if not isinstance(p3, dict):
            continue
        ge = p3.get("graph_edges")
        if ge is None:
            continue
        for e in ge:
            if isinstance(e, (list, tuple)) and len(e) >= 2:
                edges.add((str(e[0]), str(e[1])))
    return {"graph_edges": edges}
