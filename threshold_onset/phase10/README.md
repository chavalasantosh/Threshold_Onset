# Phase 10 — Directed continuation (structural)

## Position in the stack

| Layer | Location | Role |
|--------|-----------|------|
| Phases 0–4 | `threshold_onset/phase0` … `phase4` | Action, identity, structure (frozen contracts) |
| **Phase 10** | `threshold_onset/phase10` | **Directed** empirical continuation, exclusion, necessity |
| Phases 5–9 | `threshold_onset/semantic/phase5` … `phase9` | Semantic discovery (consequence field, roles, fluency, …) |

Phase 10 is **not** a semantic phase. It does not assign meaning or roles; it only summarizes what **actually followed** what in ordered identity streams.

## Inputs

- **Primary:** `Sequence[Sequence[str]]` — one time-ordered list of identity hashes per run.
- **Optional:** Phase 3 metrics with `graph_edges` when `cross_check_phase3=True` — only transitions whose endpoints appear as an undirected Phase 3 edge (in either orientation) are counted.

## Outputs (`Phase10Result`)

- `pair_counts`: `(from_id, to_id) -> count`
- `outgoing` / `incoming` marginals
- `universe_ids`: all ids appearing as source or target
- `excluded_successors[a]`: universe ids that **never** appeared as a direct successor of `a` in the sample
- `necessity_by_source[a]`: if a **single** successor strictly wins on count and `count/total >= necessity_mass_threshold`, `{"successor": ..., "mass_fraction": ...}`; else `None`. Ties on the maximum count → no necessity.

## Gate

Default: at least one directed transition (`MIN_TRANSITIONS_FOR_GATE`). If the gate fails, metrics are still computed (often empty); check `gate_passed` and `gate_reason`.

## Multi-method merge (SanTEK / several tokenizers)

When the same text is run with multiple tokenization methods, each produces its own `model_state`. Use:

```python
from threshold_onset.phase10 import run_phase10_from_method_states

method_states = [("word", ms_word), ("char", ms_char)]
r = run_phase10_from_method_states(method_states, cross_check_phase3=False)
```

`cross_check_phase3=True` unions `graph_edges` from every `phase3_metrics` before filtering. Helpers: `identity_streams_from_method_states`, `union_phase3_metrics_for_phase10` in `merge.py`.

## Integration helper

`identity_sequences_from_model_state(model_state)` builds streams from `phase2_metrics["identity_mappings"]` and `residue_sequences`, using the same segment hash as `integration/structural_prediction_loop.py`.

### `integration/run_complete.py`

When you need Phase 10 on a full pipeline run:

- Set **`include_phase10_metrics: true`** in `config/default.json` under `pipeline`, **or**
- Export **`PIPELINE_PHASE10_METRICS=1`**, **or**
- Pass CLI **`--phase10-metrics`** (with programmatic `return_model_state=True`).

Optional: **`phase10_cross_check_phase3`** / **`PIPELINE_PHASE10_CROSS_CHECK_PHASE3=1`** / **`--phase10-cross-check-phase3`** filters counts to transitions licensed by Phase 3 undirected edges.

`result.model_state["phase10_metrics"]` is the JSON blob from `Phase10Result.to_jsonable()`.

## Serialization

`Phase10Result.to_jsonable()` returns a JSON-safe dict (pair keys use `||`, see `PAIR_KEY_SEP`).

## Usage

```python
from threshold_onset.phase10 import run_phase10, Phase10Result

r: Phase10Result = run_phase10([["a", "b", "a", "b"]], necessity_mass_threshold=1.0)
assert r.gate_passed
print(r.to_jsonable())
```

```python
from threshold_onset.phase10 import run_phase10_from_model_state

r = run_phase10_from_model_state(model_state, cross_check_phase3=True)
```

## Tests

`pytest threshold_onset/phase10/tests/test_phase10.py`

## See also

- [`docs/IDENTITY_CONDITIONED_CONTINUATION.md`](../../docs/IDENTITY_CONDITIONED_CONTINUATION.md) — design for **(source, content) → outcome** (empirical; not baked halo bias).
- [`docs/MODEL_CONTRACT.md`](../../docs/MODEL_CONTRACT.md) — `model_state` shape; optional `phase10_metrics`.

### Programmatic API

`threshold_onset.api.process(..., return_model_state=True, include_phase10_metrics=True)` sets `ProcessResult.model_state` (large — use intentionally).
