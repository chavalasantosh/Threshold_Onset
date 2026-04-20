"""
Phase 10 — result container and JSON-safe serialization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from threshold_onset.phase10.constants import PAIR_KEY_SEP
from threshold_onset.phase10.directed import PairCounts


def pair_key(a: str, b: str) -> str:
    return f"{a}{PAIR_KEY_SEP}{b}"


def parse_pair_key(key: str) -> Tuple[str, str]:
    if PAIR_KEY_SEP not in key:
        raise ValueError(f"invalid pair key: {key!r}")
    a, b = key.split(PAIR_KEY_SEP, 1)
    return a, b


@dataclass(frozen=True)
class Phase10Result:
    """
    Immutable snapshot of directed continuation analytics.

    Note: dict values remain mutable objects; treat as logically immutable
    after construction (do not mutate in place in production pipelines).
    """

    gate_passed: bool
    gate_reason: str
    total_transitions: int
    cross_check_phase3: bool
    necessity_mass_threshold: float
    pair_counts: PairCounts
    outgoing: Dict[str, Dict[str, int]]
    incoming: Dict[str, Dict[str, int]]
    universe_ids: Tuple[str, ...]
    necessity_by_source: Dict[str, Optional[Dict[str, object]]]
    excluded_successors: Dict[str, Tuple[str, ...]] = field(default_factory=dict)

    def to_jsonable(self) -> Dict[str, Any]:
        """Deterministic, JSON-serializable dict (sorted keys where applicable)."""
        pc = {pair_key(a, b): int(c) for (a, b), c in sorted(self.pair_counts.items())}
        out_going = {k: dict(sorted(v.items())) for k, v in sorted(self.outgoing.items())}
        in_coming = {k: dict(sorted(v.items())) for k, v in sorted(self.incoming.items())}
        excl = {k: list(v) for k, v in sorted(self.excluded_successors.items())}
        nec = {k: (dict(sorted(v.items())) if v else None) for k, v in sorted(self.necessity_by_source.items())}
        return {
            "phase": "phase10",
            "gate_passed": self.gate_passed,
            "gate_reason": self.gate_reason,
            "total_transitions": self.total_transitions,
            "cross_check_phase3": self.cross_check_phase3,
            "necessity_mass_threshold": self.necessity_mass_threshold,
            "pair_counts": pc,
            "outgoing": out_going,
            "incoming": in_coming,
            "universe_ids": list(self.universe_ids),
            "necessity_by_source": nec,
            "excluded_successors": excl,
        }

    @staticmethod
    def from_jsonable(payload: Dict[str, Any]) -> "Phase10Result":
        """Round-trip helper for persisted metrics (best-effort validation)."""
        raw_pc = payload.get("pair_counts") or {}
        pair_counts: PairCounts = {}
        for k, c in raw_pc.items():
            a, b = parse_pair_key(str(k))
            pair_counts[(a, b)] = int(c)
        ex = payload.get("excluded_successors") or {}
        excluded = {str(k): tuple(str(x) for x in v) for k, v in sorted(ex.items())}
        return Phase10Result(
            gate_passed=bool(payload["gate_passed"]),
            gate_reason=str(payload.get("gate_reason") or ""),
            total_transitions=int(payload["total_transitions"]),
            cross_check_phase3=bool(payload.get("cross_check_phase3", False)),
            necessity_mass_threshold=float(payload.get("necessity_mass_threshold", 1.0)),
            pair_counts=pair_counts,
            outgoing={str(k): {str(x): int(y) for x, y in v.items()} for k, v in (payload.get("outgoing") or {}).items()},
            incoming={str(k): {str(x): int(y) for x, y in v.items()} for k, v in (payload.get("incoming") or {}).items()},
            universe_ids=tuple(str(x) for x in (payload.get("universe_ids") or [])),
            necessity_by_source={
                str(k): (None if v is None else dict(v))
                for k, v in (payload.get("necessity_by_source") or {}).items()
            },
            excluded_successors=excluded,
        )
