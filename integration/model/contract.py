"""
Model API contract: types and invariants.

See docs/MODEL_CONTRACT.md for full contract.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# Symbol: same as Phase 4 identity alias (int in current implementation)
Symbol = Any
PathScores = Dict[Tuple[Symbol, Symbol], float]


def model_state_from_pipeline(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and return state dict for model use.
    Raises ValueError if required keys are missing.
    """
    required = ("phase2_metrics", "phase3_metrics", "phase4_metrics", "path_scores", "tokens")
    missing = [k for k in required if k not in state]
    if missing:
        raise ValueError(f"ModelState missing required keys: {missing}")
    return state


def path_scores_copy(scores: PathScores) -> PathScores:
    """Return a mutable copy of path_scores. Contract: learning only mutates copies."""
    return dict(scores)
