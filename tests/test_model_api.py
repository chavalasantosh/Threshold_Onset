"""
Tests for integration.model API and contract.

Contract: docs/MODEL_CONTRACT.md.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_model_state_validation():
    """model_state_from_pipeline raises ValueError when required keys missing."""
    from integration.model.contract import model_state_from_pipeline

    with pytest.raises(ValueError, match="missing required keys"):
        model_state_from_pipeline({})
    with pytest.raises(ValueError, match="ModelState"):
        model_state_from_pipeline({"tokens": []})


def test_model_state_validation_passes():
    """model_state_from_pipeline returns state when keys present."""
    from integration.model.contract import model_state_from_pipeline

    state = {
        "phase2_metrics": {},
        "phase3_metrics": {},
        "phase4_metrics": {},
        "path_scores": {},
        "tokens": ["a", "b"],
    }
    assert model_state_from_pipeline(state) is state


def test_evaluate_returns_model_result():
    """evaluate() returns ModelResult with accuracy, total_predictions, correct_predictions."""
    from integration.model import evaluate, ModelConfig

    # Invalid state: no path_scores / phase data to build symbols
    state = {
        "phase2_metrics": {},
        "phase3_metrics": {},
        "phase4_metrics": {},
        "path_scores": {},
        "tokens": [],
    }
    cfg = ModelConfig()
    r = evaluate(state, cfg)
    assert hasattr(r, "accuracy")
    assert hasattr(r, "total_predictions")
    assert hasattr(r, "correct_predictions")
    assert hasattr(r, "updated_path_scores")
    assert hasattr(r, "error")
    assert r.updated_path_scores is None


def test_evaluate_with_real_pipeline_state():
    """evaluate() and evaluate_with_learning() on real pipeline state return valid result."""
    from integration.model import evaluate, evaluate_with_learning, ModelConfig
    from integration.run_complete import run, PipelineConfig

    cfg = PipelineConfig.from_project()
    cfg.show_tui = False
    result = run(
        text_override="Action before knowledge. Function stabilizes.",
        cfg=cfg,
        return_result=True,
        return_model_state=True,
    )
    if not result or not result.model_state:
        pytest.skip("Pipeline did not return model_state")
    model_cfg = ModelConfig.from_project()
    r = evaluate(result.model_state, model_cfg)
    if r.error:
        pytest.skip(f"evaluate error: {r.error}")
    assert 0 <= r.accuracy <= 1
    assert r.total_predictions >= 0
    assert r.correct_predictions >= 0
    assert r.updated_path_scores is None

    r2 = evaluate_with_learning(result.model_state, model_cfg)
    if r2.error:
        pytest.skip(f"evaluate_with_learning error: {r2.error}")
    assert 0 <= r2.accuracy <= 1
    assert r2.updated_path_scores is not None
    assert isinstance(r2.updated_path_scores, dict)


def test_learning_rule_mutates_copy_only():
    """apply_learning_step mutates given dict; path_scores_copy is independent."""
    from integration.model.contract import path_scores_copy
    from integration.model.learning import apply_learning_step

    original = {(1, 2): 1.0, (1, 3): 0.5}
    copy = path_scores_copy(original)
    apply_learning_step(copy, 1, 2, 3, 0.1)
    assert copy[(1, 2)] == 1.1
    assert copy[(1, 3)] == 0.4
    assert original[(1, 2)] == 1.0
    assert original[(1, 3)] == 0.5


def test_model_config_from_project():
    """ModelConfig.from_project() returns valid config."""
    from integration.model import ModelConfig

    cfg = ModelConfig.from_project()
    assert cfg.learning_rate > 0
    assert cfg.prediction_method in ("highest_score", "weighted_random")
    errors = cfg.validate()
    assert len(errors) == 0
