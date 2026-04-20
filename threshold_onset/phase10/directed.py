"""
Phase 10 — directed successor counting from ordered identity streams.

Counts (from_id, to_id) along each sequence. Optional cross-check with Phase 3
undirected structural edges (both orientations) to restrict which transitions
are admitted into the empirical directed index.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Optional, Sequence, Set, Tuple

PairCounts = Dict[Tuple[str, str], int]


def phase3_undirected_edge_lookup(phase3_metrics: Optional[Dict[str, Any]]) -> Optional[Set[Tuple[str, str]]]:
    """
    Build a directed-style lookup set from Phase 3's undirected edge list.

    Each undirected edge {a, b} yields both (a, b) and (b, a) so a directed
    transition A→B is kept only if Phase 3 saw A and B as adjacent in either order.
    """
    if not phase3_metrics:
        return None
    edges = phase3_metrics.get("graph_edges") or set()
    undirected: Set[Tuple[str, str]] = set()
    for e in edges:
        if isinstance(e, (list, tuple)) and len(e) >= 2:
            a, b = str(e[0]), str(e[1])
            undirected.add((a, b))
            undirected.add((b, a))
    return undirected if undirected else None


def build_directed_counts(
    identity_sequences: Sequence[Sequence[str]],
    *,
    cross_check_phase3: bool = False,
    phase3_metrics: Optional[Dict[str, Any]] = None,
) -> Tuple[PairCounts, int]:
    """
    Count ordered transitions (A, B) along each stream.

    Self-loops A→A are counted when consecutive mapped identities match.

    Returns:
        pair_counts: (from_id, to_id) -> occurrence count
        total_transitions: sum of counts
    """
    pair_counts: DefaultDict[Tuple[str, str], int] = defaultdict(int)
    edge_filter = phase3_undirected_edge_lookup(phase3_metrics) if cross_check_phase3 else None

    for stream in identity_sequences:
        if len(stream) < 2:
            continue
        for i in range(len(stream) - 1):
            a, b = str(stream[i]), str(stream[i + 1])
            if edge_filter is not None and (a, b) not in edge_filter:
                continue
            pair_counts[(a, b)] += 1

    total = int(sum(pair_counts.values()))
    return dict(pair_counts), total


def marginal_outgoing(pair_counts: PairCounts) -> Dict[str, Dict[str, int]]:
    """from_id -> {to_id: count}."""
    out: DefaultDict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for (a, b), c in pair_counts.items():
        out[a][b] += int(c)
    return {k: dict(v) for k, v in out.items()}


def marginal_incoming(pair_counts: PairCounts) -> Dict[str, Dict[str, int]]:
    """to_id -> {from_id: count}."""
    inc: DefaultDict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for (a, b), c in pair_counts.items():
        inc[b][a] += int(c)
    return {k: dict(v) for k, v in inc.items()}


def universe_from_pair_counts(pair_counts: PairCounts) -> List[str]:
    """All identity ids that appear as either source or target in pair_counts."""
    ids: Set[str] = set()
    for (a, b) in pair_counts:
        ids.add(a)
        ids.add(b)
    return sorted(ids)
