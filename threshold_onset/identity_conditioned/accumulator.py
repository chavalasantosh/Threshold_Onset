"""
Empirical counts for (source_id, content_id) -> outcome_key.

See docs/IDENTITY_CONDITIONED_CONTINUATION.md. No priors or reputation scalars —
only observed triples.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, DefaultDict, Dict, List, Mapping, Tuple


Triple = Tuple[str, str, str]  # source_id, content_id, outcome_key


@dataclass
class IdentityConditionedAccumulator:
    """
    Thread-unsafe unless externally locked. Counts occurrences of
    (source_id, content_id, outcome_key).
    """

    _counts: DefaultDict[Triple, int] = field(
        default_factory=lambda: defaultdict(int)
    )

    def record(
        self,
        source_id: str,
        content_id: str,
        outcome_key: str,
        *,
        weight: int = 1,
    ) -> None:
        if weight <= 0:
            raise ValueError("weight must be positive")
        s, c, o = str(source_id), str(content_id), str(outcome_key)
        self._counts[(s, c, o)] += int(weight)

    def count(
        self,
        source_id: str,
        content_id: str,
        outcome_key: str,
    ) -> int:
        return int(self._counts.get((str(source_id), str(content_id), str(outcome_key)), 0))

    def total_for_pair(self, source_id: str, content_id: str) -> int:
        s, c = str(source_id), str(content_id)
        return sum(
            n for (a, b, _), n in self._counts.items() if a == s and b == c
        )

    def outcome_distribution(
        self,
        source_id: str,
        content_id: str,
    ) -> Dict[str, int]:
        """outcome_key -> count for fixed (source, content)."""
        s, c = str(source_id), str(content_id)
        out: Dict[str, int] = {}
        for (a, b, o), n in self._counts.items():
            if a == s and b == c:
                out[o] = out.get(o, 0) + int(n)
        return dict(sorted(out.items()))

    def to_jsonable(self) -> Dict[str, Any]:
        """Deterministic JSON-safe dict."""
        rows: List[Dict[str, Any]] = []
        for (s, c, o), n in sorted(self._counts.items()):
            rows.append({"source_id": s, "content_id": c, "outcome_key": o, "count": int(n)})
        return {
            "layer": "identity_conditioned",
            "version": 1,
            "rows": rows,
            "distinct_triples": len(self._counts),
        }

    @staticmethod
    def from_jsonable(payload: Mapping[str, Any]) -> "IdentityConditionedAccumulator":
        acc = IdentityConditionedAccumulator()
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            w = int(row.get("count") or 0)
            if w <= 0:
                continue
            acc.record(
                str(row.get("source_id", "")),
                str(row.get("content_id", "")),
                str(row.get("outcome_key", "")),
                weight=w,
            )
        return acc
