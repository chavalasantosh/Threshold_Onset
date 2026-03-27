"""
Predict next identity: symbol sequence from state, single-step prediction.

Contract: see docs/MODEL_CONTRACT.md. No mutation of state.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from integration.model.contract import PathScores, Symbol


def symbol_sequence_from_state(state: Dict[str, Any]) -> List[Symbol]:
    """
    Derive symbol sequence from model state (tokens + Phase 2/3/4).
    Pure function: no mutation. Uses ContinuationObserver and TokenAction.
    """
    from integration.continuation_observer import ContinuationObserver  # type: ignore
    from integration.unified_system import TokenAction  # type: ignore

    phase2 = state["phase2_metrics"]
    phase3 = state["phase3_metrics"]
    phase4 = state["phase4_metrics"]
    tokens = state["tokens"]

    observer = ContinuationObserver(phase4, phase3, phase2)
    action = TokenAction(tokens)
    symbols: List[Symbol] = []
    current_identity_hash = None

    for _ in range(len(tokens) * 2):
        residue = action()
        next_identity_hash = observer._residue_to_identity_hash(residue)  # pylint: disable=protected-access
        if next_identity_hash is None:
            continue
        next_symbol = observer._identity_hash_to_symbol(next_identity_hash)  # pylint: disable=protected-access
        if next_symbol is None:
            continue
        if current_identity_hash != next_identity_hash:
            symbols.append(next_symbol)
            current_identity_hash = next_identity_hash

    return symbols


def predict_next(
    current: Symbol,
    path_scores: PathScores,
    method: str = "highest_score",
) -> Optional[Symbol]:
    """
    Single-step prediction: choose next symbol from path_scores.
    Delegates to integration.scoring.choose_next_path. No mutation.
    """
    from integration.scoring import choose_next_path  # type: ignore
    return choose_next_path(current, path_scores, method=method)
