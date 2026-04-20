"""
Phase 10 — extract ordered identity streams from pipeline-shaped state.

Segment hashing matches ``integration/structural_prediction_loop.py`` and
Phase 2's residue pairing convention: MD5 of ``str((r_a, r_b))``.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Mapping, Sequence


def segment_hash_residue_pair(r_a: float, r_b: float) -> str:
    """MD5 hex digest for a length-2 residue window (must match structural_prediction_loop)."""
    return hashlib.md5(str((r_a, r_b)).encode("utf-8")).hexdigest()


def identity_sequence_from_residue_run(
    residue_run: Sequence[float],
    identity_mappings: Mapping[str, str],
) -> List[str]:
    """
    Map a residue run to the sequence of identity hashes at each consecutive pair.

    Only pairs with a known segment hash in ``identity_mappings`` contribute.
    """
    if len(residue_run) < 2:
        return []
    out: List[str] = []
    for i in range(len(residue_run) - 1):
        h = segment_hash_residue_pair(float(residue_run[i]), float(residue_run[i + 1]))
        ident = identity_mappings.get(h)
        if ident is not None:
            out.append(str(ident))
    return out


def identity_sequences_from_model_state(model_state: Mapping[str, Any]) -> List[List[str]]:
    """
    Build one identity stream per residue run using Phase 2 mappings.

    Missing or empty fields yield empty lists (caller may still run Phase 10;
    gate will fail if no transitions).
    """
    p2 = model_state.get("phase2_metrics") or {}
    if not isinstance(p2, dict):
        return []
    maps = p2.get("identity_mappings") or {}
    if not isinstance(maps, dict):
        maps = {}
    runs = model_state.get("residue_sequences") or []
    if not isinstance(runs, (list, tuple)):
        return []

    streams: List[List[str]] = []
    for run in runs:
        if not isinstance(run, (list, tuple)):
            continue
        try:
            floats = [float(x) for x in run]
        except (TypeError, ValueError):
            continue
        streams.append(identity_sequence_from_residue_run(floats, maps))
    return streams
