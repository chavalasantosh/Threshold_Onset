"""
Model API: predict-next identity objective, optional learning rule.

Contract: docs/MODEL_CONTRACT.md.
Entry points: evaluate(), evaluate_with_learning().
SanTEK base model (canonical): train, generate, eval_held_out — integration.model.santek_base.
Config: ModelConfig.from_project().
"""

from integration.model.api import ModelResult, evaluate, evaluate_with_learning
from integration.model.base_model import load_base_model, save_base_model
from integration.model.config import ModelConfig
from integration.model.contract import model_state_from_pipeline, path_scores_copy
from integration.model.learning import apply_learning_step
from integration.model.predict import predict_next, symbol_sequence_from_state
from integration.model.dataset import (
    CorpusRecord,
    SplitManifest,
    load_and_split,
    load_jsonl_corpus,
    split_train_val_test,
    texts_from_records,
)
from integration.model.generator import (
    generate_symbols_with_cycle_control,
    is_anchored,
    last_connected_anchor,
    symbols_to_text as generator_symbols_to_text,
)
from integration.model.santek_base import (
    EvalResult,
    SantekModel,
    eval_held_out,
    generate as santek_generate,
    is_prompt_connected,
    load_santek_model,
    save_santek_model,
    train as santek_train,
)

__all__ = [
    "CorpusRecord",
    "SplitManifest",
    "load_and_split",
    "load_jsonl_corpus",
    "split_train_val_test",
    "texts_from_records",
    "generate_symbols_with_cycle_control",
    "is_anchored",
    "last_connected_anchor",
    "generator_symbols_to_text",
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
    "SantekModel",
    "santek_train",
    "santek_generate",
    "load_santek_model",
    "save_santek_model",
    "eval_held_out",
    "EvalResult",
    "is_prompt_connected",
    "CorpusRecord",
    "SplitManifest",
    "load_and_split",
    "load_jsonl_corpus",
    "split_train_val_test",
    "texts_from_records",
    "generate_symbols_with_cycle_control",
    "is_anchored",
    "last_connected_anchor",
    "generator_symbols_to_text",
]
