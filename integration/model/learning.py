"""
Learning rule: update path scores from prediction outcome.

Contract: only mutates the provided scores dict (a copy). See docs/MODEL_CONTRACT.md.
"""

from __future__ import annotations

from integration.model.contract import PathScores, Symbol


def apply_learning_step(
    scores: PathScores,
    current: Symbol,
    actual_next: Symbol,
    predicted_next: Symbol,
    eta: float,
) -> None:
    """
    Update scores in-place: reward (current, actual_next);
    penalize (current, predicted_next) if wrong.
    Invariant: eta > 0; scores is a mutable copy.
    """
    key_actual = (current, actual_next)
    key_pred = (current, predicted_next)
    scores[key_actual] = scores.get(key_actual, 0.0) + eta
    if key_pred != key_actual:
        scores[key_pred] = scores.get(key_pred, 0.0) - eta
