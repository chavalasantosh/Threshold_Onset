"""
Phase 10 — necessity and exclusion derived from directed marginals.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Tuple

from threshold_onset.phase10.directed import PairCounts, marginal_incoming, marginal_outgoing


def dominant_successor(
    counts: Mapping[str, int],
    mass_threshold: float,
) -> Optional[Tuple[str, float]]:
    """
    If one successor strictly wins count and mass_fraction >= threshold, return it.

    Ties on the maximum count yield None (no necessity under this rule).
    """
    if not counts:
        return None
    if mass_threshold <= 0.0 or mass_threshold > 1.0:
        raise ValueError("mass_threshold must be in (0, 1]")

    total = sum(int(v) for v in counts.values())
    if total <= 0:
        return None

    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    best_id, best_c = ranked[0]
    second_c = int(ranked[1][1]) if len(ranked) > 1 else 0
    if best_c == second_c:
        return None

    ratio = float(best_c) / float(total)
    if ratio + 1e-15 < mass_threshold:
        return None
    return (best_id, ratio)


def necessity_by_source(
    outgoing: Mapping[str, Mapping[str, int]],
    mass_threshold: float,
) -> Dict[str, Optional[Dict[str, object]]]:
    """
    Per source id: None or a JSON-friendly dict with successor and mass_fraction.
    """
    out: Dict[str, Optional[Dict[str, object]]] = {}
    for src, succ in outgoing.items():
        dom = dominant_successor(succ, mass_threshold)
        if dom is None:
            out[src] = None
        else:
            sid, frac = dom
            out[src] = {"successor": sid, "mass_fraction": frac}
    return out


def excluded_successors(
    universe: List[str],
    outgoing: Mapping[str, Mapping[str, int]],
) -> Dict[str, List[str]]:
    """
    For each id in the universe, list ids that never appeared as a direct successor.

    Sources with no outgoing mass list every other universe member as excluded
    (including self if self never appears as successor from self).
    """
    u_set = set(universe)
    result: Dict[str, List[str]] = {}
    for a in universe:
        seen = set((outgoing.get(a) or {}).keys())
        result[a] = sorted(u_set - seen)
    return result


def build_marginals(pair_counts: PairCounts) -> Tuple[Dict[str, Dict[str, int]], Dict[str, Dict[str, int]]]:
    return marginal_outgoing(pair_counts), marginal_incoming(pair_counts)
