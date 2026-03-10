"""
Model API: evaluate and evaluate_with_learning.

Contract: docs/MODEL_CONTRACT.md. Entry points take ModelState and ModelConfig.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from integration.model.config import ModelConfig
from integration.model.contract import model_state_from_pipeline, path_scores_copy
from integration.model.learning import apply_learning_step
from integration.model.predict import predict_next, symbol_sequence_from_state


@dataclass
class ModelResult:
    """Result of evaluate or evaluate_with_learning."""
    accuracy: float
    total_predictions: int
    correct_predictions: int
    updated_path_scores: Optional[Dict[tuple, float]] = None  # None when learning off
    error: Optional[str] = None  # When accuracy is undefined, error message


def evaluate(
    state: Dict[str, Any],
    config: ModelConfig,
) -> ModelResult:
    """
    Compute next-identity prediction accuracy over state. No learning; state read-only.
    """
    try:
        model_state_from_pipeline(state)
    except ValueError as e:
        return ModelResult(
            accuracy=0.0,
            total_predictions=0,
            correct_predictions=0,
            error=str(e),
        )

    symbols = symbol_sequence_from_state(state)
    if len(symbols) < 2:
        return ModelResult(
            accuracy=0.0,
            total_predictions=0,
            correct_predictions=0,
            error="Symbol sequence too short (need at least 2 symbols).",
        )

    path_scores = state["path_scores"]
    correct = 0
    total = 0
    for i in range(len(symbols) - 1):
        current = symbols[i]
        actual_next = symbols[i + 1]
        pred = predict_next(current, path_scores, method=config.prediction_method)
        if pred is not None:
            total += 1
            if pred == actual_next:
                correct += 1

    if total == 0:
        return ModelResult(
            accuracy=0.0,
            total_predictions=0,
            correct_predictions=0,
            error="No valid predictions (no scored paths from any symbol).",
        )

    return ModelResult(
        accuracy=correct / total,
        total_predictions=total,
        correct_predictions=correct,
        updated_path_scores=None,
    )


def evaluate_with_learning(
    state: Dict[str, Any],
    config: ModelConfig,
) -> ModelResult:
    """
    Same as evaluate, but apply learning rule to a copy of path_scores during the pass.
    Returns updated_path_scores (caller may persist or feed into next run). Original state unchanged.
    """
    try:
        model_state_from_pipeline(state)
    except ValueError as e:
        return ModelResult(
            accuracy=0.0,
            total_predictions=0,
            correct_predictions=0,
            error=str(e),
        )

    symbols = symbol_sequence_from_state(state)
    if len(symbols) < 2:
        return ModelResult(
            accuracy=0.0,
            total_predictions=0,
            correct_predictions=0,
            error="Symbol sequence too short (need at least 2 symbols).",
        )

    scores = path_scores_copy(state["path_scores"])
    correct = 0
    total = 0
    for i in range(len(symbols) - 1):
        current = symbols[i]
        actual_next = symbols[i + 1]
        pred = predict_next(current, scores, method=config.prediction_method)
        if pred is not None:
            total += 1
            if pred == actual_next:
                correct += 1
            apply_learning_step(
                scores, current, actual_next, pred, config.learning_rate
            )

    if total == 0:
        return ModelResult(
            accuracy=0.0,
            total_predictions=0,
            correct_predictions=0,
            error="No valid predictions (no scored paths from any symbol).",
        )

    return ModelResult(
        accuracy=correct / total,
        total_predictions=total,
        correct_predictions=correct,
        updated_path_scores=scores,
    )
