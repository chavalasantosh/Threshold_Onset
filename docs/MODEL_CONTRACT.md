# Model API Contract

**Status:** Contract (implementation in `integration/model/`)  
**Objective:** Predict next identity. Single task, single metric (accuracy), optional learning rule.

---

## 1. Purpose

The model layer exposes a **predict-next-identity** objective over the pipeline state produced by `run_complete.run(..., return_model_state=True)`. It does not replace or modify Phases 0–4 or 5–9; it consumes their outputs and (optionally) updates **path scores** via a defined learning rule.

---

## 2. Inputs (read-only from pipeline)

The model consumes a **ModelState** (the same structure as `PipelineResult.model_state` when `return_model_state=True`). No other pipeline internals.

| Key | Type | Source | Description |
|-----|------|--------|--------------|
| `phase2_metrics` | `Dict[str, Any]` | Phase 2 | Identity mappings, persistent segment hashes. |
| `phase3_metrics` | `Dict[str, Any]` | Phase 3 | Graph, persistent relation hashes. |
| `phase4_metrics` | `Dict[str, Any]` | Phase 4 | identity_to_symbol, symbol_to_identity, relation_to_symbol, symbol_to_relation. |
| `path_scores` | `Dict[Tuple[Symbol, Symbol], float]` | Scoring | (from_symbol, to_symbol) → score. Tuple keys, float values only. |
| `tokens` | `List[str]` | Tokenization | Token sequence for the input text. |
| `residue_sequences` | `List[List[float]]` | Phase 0 | Residue sequences (optional for some entry points). |
| `phase10_metrics` | `Dict[str, Any]` | Phase 10 (optional) | Present when `PipelineConfig.include_phase10_metrics` is True and `return_model_state=True`. JSON-shaped directed continuation snapshot (`to_jsonable()`). The model API ignores this key. |

**Invariant:** The model never mutates `phase2_metrics`, `phase3_metrics`, `phase4_metrics`, or `tokens`. It may only mutate a **copy** of `path_scores` when learning is enabled.

---

## 3. Outputs

| Output | Type | Description |
|--------|------|--------------|
| **accuracy** | `float` | In [0, 1]. Fraction of positions where predicted next symbol equals actual next. |
| **total_predictions** | `int` | Number of positions where a prediction was made (allowed transition existed). |
| **correct_predictions** | `int` | Number of correct predictions. |
| **updated_path_scores** | `Optional[Dict[Tuple[Symbol, Symbol], float]]` | When learning is on, a new dict of updated scores; otherwise None. |

Symbol type is the same as used in Phase 4 (identity alias); in practice int or str depending on alias implementation. The model uses the same type as the keys of `path_scores`.

---

## 4. Learning rule (invariant)

When learning is enabled:

1. **Correct prediction:** `path_scores[(current, actual_next)] += eta`.
2. **Wrong prediction:** `path_scores[(current, predicted_next)] -= eta` and `path_scores[(current, actual_next)] += eta`.

Updates apply only to a **mutable copy** of `path_scores`. The original state is never modified. `eta` is a positive float from config (default 0.1).

---

## 5. Entry points (API)

- **`evaluate(state: ModelState, config: ModelConfig) -> ModelResult`**  
  Computes accuracy (and optionally total/correct) over the symbol sequence derived from `state`. No learning; state is read-only.

- **`evaluate_with_learning(state: ModelState, config: ModelConfig) -> ModelResult`**  
  Same as evaluate, but applies the learning rule to a copy of `path_scores` during the pass. Returns accuracy and the updated path_scores (caller may persist or feed into a future run).

- **`symbol_sequence_from_state(state: ModelState) -> List[Symbol]`**  
  Pure function: tokens + observer built from state → symbol sequence. Used internally; exposed for tests and baselines.

- **`predict_next(symbol: Symbol, path_scores: PathScores, method: str) -> Optional[Symbol]`**  
  Single-step prediction. Delegates to the same scoring/ranking used by the pipeline (e.g. `choose_next_path`). No magic.

Config (`ModelConfig`) supplies: `learning_rate` (eta), `prediction_method` ("highest_score" or "weighted_random"), and any future options. Loaded from `config/default.json` under key `model` with sensible defaults.

---

## 6. Integration

- **Pipeline:** `run_complete.run(..., return_model_state=True)` returns `PipelineResult.model_state`. That dict is a valid `ModelState` for this contract. The model module does not call `run()`; the caller passes state in. **Async:** `run_complete.async_run(..., return_model_state=True)` mirrors the same behavior.
- **Config:** Model section in project config; `ModelConfig.from_project()` or equivalent. Pipeline config may remain unchanged; model config is separate.
- **Script:** `integration/model_predict_next.py` becomes a thin CLI: parse args → load pipeline config → call `run(..., return_model_state=True)` → call `integration.model.api.evaluate` or `evaluate_with_learning` → print result. No business logic in the script.

---

## 7. No magic

- No implicit global state. All inputs passed in (state, config).
- No mutation of pipeline outputs. Learning updates a copy of path_scores only.
- Types: ModelState, ModelConfig, ModelResult are dataclasses or TypedDicts; public functions are typed.
- Tests: contract tests (input/output shape), accuracy on fixed sequence, learning rule effect.
