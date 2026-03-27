# integration.model

Predict-next-identity model over pipeline state. Contract: `docs/MODEL_CONTRACT.md`.

## Entry points

- **`evaluate(state, config) -> ModelResult`** — Accuracy only; state read-only.
- **`evaluate_with_learning(state, config) -> ModelResult`** — Accuracy + updated path_scores (learning rule applied to a copy).

## Config

```python
from integration.model import ModelConfig
cfg = ModelConfig.from_project()  # loads config/default.json ["model"]
```

Options: `learning_rate` (eta), `prediction_method` ("highest_score" | "weighted_random").

## Usage

State comes from the pipeline; the model does not run the pipeline.

```python
from integration.run_complete import run, PipelineConfig
from integration.model import evaluate, evaluate_with_learning, ModelConfig

cfg = PipelineConfig.from_project()
cfg.show_tui = False
result = run("Your text.", cfg=cfg, return_result=True, return_model_state=True)
if result and result.model_state:
    model_cfg = ModelConfig.from_project()
    r = evaluate(result.model_state, model_cfg)
    print(r.accuracy, r.total_predictions, r.correct_predictions)
```

## Types

- `ModelResult`: accuracy, total_predictions, correct_predictions, updated_path_scores (optional), error (optional).
- State: dict with phase2_metrics, phase3_metrics, phase4_metrics, path_scores, tokens, residue_sequences (see contract). Optional `phase10_metrics` when `PipelineConfig.include_phase10_metrics` is True.
