"""
Model API: predict-next identity objective, optional learning rule.

Contract: docs/MODEL_CONTRACT.md.
Entry points: evaluate(), evaluate_with_learning().
Config: ModelConfig.from_project().
"""

from integration.model.api import ModelResult, evaluate, evaluate_with_learning
from integration.model.base_model import load_base_model, save_base_model
from integration.model.config import ModelConfig
from integration.model.contract import model_state_from_pipeline, path_scores_copy
from integration.model.learning import apply_learning_step
from integration.model.predict import predict_next, symbol_sequence_from_state

__all__ = [
    "evaluate",
    "evaluate_with_learning",
    "ModelResult",
    "ModelConfig",
    "model_state_from_pipeline",
    "path_scores_copy",
    "apply_learning_step",
    "predict_next",
    "symbol_sequence_from_state",
    "save_base_model",
    "load_base_model",
]
