# Recent developments — consolidated summary

Single inventory of **new layers, integrations, configuration, env vars, docs, and tests** shipped in the Phase 10 / model-state / API / SanTEK / semantic-provenance wave. For frozen phase doctrine, still use `docs/PHASE_STATUS_CANONICAL.md` and `docs/CANONICAL_PHASE_MAP.md`.

---

## Quick index

| Area | Section |
|------|---------|
| Package version & top-level exports | §1 |
| Phase 10 module (full public API) | §2 |
| `model_state` shape & model contract | §3 |
| `run_complete`: sync + async, config, CLI, env | §4 |
| `threshold_onset.api.process` behavior | §5 |
| HTTP `scripts/health_server.py` | §6 |
| CLI `-m threshold_onset` (config / health) | §7 |
| `integration/model` predict-next API | §8 |
| SanTEK (`santek_base.py`): checkpoints, Phase 10, env | §9 |
| Root `santek_base_model.py` | §10 |
| Semantic wiring (Phase 5 metadata, scripts) | §11 |
| Other integration scripts | §12 |
| Identity-conditioned layer | §13 |
| `config/default.json` | §14 |
| Documentation files touched or added | §15 |
| Removed duplicate `threshold_onset.phase5` | §16 |
| Test matrix (`tests/` + package tests) | §17 |
| Gaps / not auto-wired | §18 |

---

## 1. Package surface

- **`threshold_onset` v1.2.0** — `threshold_onset/__init__.py` re-exports a **small** subset:
  - `Phase10Result`, `run_phase10`, `run_phase10_from_model_state`, `phase10_jsonable_from_model_state`
  - `IdentityConditionedAccumulator`
- **Full Phase 10 surface** lives on **`threshold_onset.phase10`** (`__all__` in `threshold_onset/phase10/__init__.py`): e.g. `run_phase10_from_method_states`, `identity_streams_from_method_states`, `union_phase3_metrics_for_phase10`, `identity_sequences_from_model_state`, directed-count helpers, `Phase10Result`, constants.

---

## 2. Phase 10 (structural directed continuation)

**Path:** `threshold_onset/phase10/`

**Role:** Read-only analytics on **ordered identity streams** after Phases 0–4: directed successor counts, empirical **exclusion**, strict-dominance **necessity**, optional **Phase 3 undirected** cross-check. **Not** semantic Phases 5–9.

**Entry points:**

- `run_phase10(streams, ...)` — raw identity-id streams.
- `run_phase10_from_model_state(model_state, cross_check_phase3=...)` — single tokenizer / single `model_state`.
- `run_phase10_from_method_states(method_states, ...)` — **multi-tokenizer**: merge Phase 3 edges, build streams per method; used by SanTEK workers and `merge.py` helpers.
- `phase10_jsonable_from_model_state(model_state)` — cheap snapshot dict for metadata (used by semantic scripts).

**Modules:** `engine.py`, `types.py`, `analysis.py`, `directed.py`, `merge.py`, `extract.py`, `constants.py`, `README.md`.

**Tests:** `threshold_onset/phase10/tests/test_phase10.py`.

**Caveat:** Same **content** from two **sources** needs explicit **`content_id`** + logging (`docs/IDENTITY_CONDITIONED_CONTINUATION.md`); Phase 10 alone is identity-stream statistics.

---

## 3. `model_state` and model contract

When `integration.run_complete.run(..., return_model_state=True)` succeeds, `PipelineResult.model_state` is a dict used by predict-next and optional Phase 10.

**Required for predict-next** (see `integration/model/contract.py` + `docs/MODEL_CONTRACT.md`):

- `phase2_metrics`, `phase3_metrics`, `phase4_metrics`, `path_scores`, `tokens`

**Commonly present from pipeline:**

- `residue_sequences` — used to build symbol sequences for semantic / structural tools.

**Optional:**

- `phase10_metrics` — present iff `PipelineConfig.include_phase10_metrics` is True **and** Phase 10 runs on that state; JSON from `Phase10Result.to_jsonable()`. **Predict-next ignores this key** (provenance / analytics only).

---

## 4. Pipeline (`integration/run_complete.py`)

**`PipelineConfig`** (relevant fields):

- `include_phase10_metrics: bool` — attach `phase10_metrics` when building `model_state`.
- `phase10_cross_check_phase3: bool` — restrict directed counts to transitions licensed by Phase 3 undirected edges.

**Environment (merged into config):**

- `PIPELINE_PHASE10_METRICS` → `include_phase10_metrics` (`1` / `true` / `yes`)
- `PIPELINE_PHASE10_CROSS_CHECK_PHASE3` → `phase10_cross_check_phase3` (same truthy set)

**CLI:**

- `--phase10-metrics`, `--phase10-cross-check-phase3` (see argparse epilog for examples).

**Async:**

- `async def async_run(..., return_result=True, return_model_state=False)` — `run_in_executor` wrapper around sync `run()`; **same** `model_state` / optional `phase10_metrics` behavior when config enables Phase 10.

**CLI async mode:** `PIPELINE_ASYNC=1` or `--async` (see `run_complete` help).

---

## 5. `threshold_onset.api.process`

**Signature:** `process(text, config=None, *, max_input_length=..., timeout_seconds=..., silent=True, trace_id=None, return_model_state=False, include_phase10_metrics=False)`.

**Behavior:**

- Loads `integration.run_complete` via import; ensures `integration/` and project root on `sys.path`.
- Builds `PipelineConfig.from_project()`, applies `config["pipeline"]` overrides for tokenization / num_runs; sets `include_phase10_metrics` when requested.
- **`silent=True`:** redirects stdout/stderr during the run.
- **`timeout_seconds` > 0:** runs pipeline in a `ThreadPoolExecutor` with `future.result(timeout=...)`; timeouts → `ProcessResult` with `error_code="runtime_timeout"`.
- **Structured logging:** JSON lines for `process_started`, `process_succeeded`, `process_failed`, `process_timeout`, etc., with `trace_id`.
- **`ValidationError`** on empty input or length over effective max (from config `pipeline.max_input_length` when present).
- Effective API timeout key in config: `pipeline.api_timeout_seconds` (see `_resolve_pipeline_settings`).

**`ProcessResult`:** `to_dict()` includes `model_state` when set.

---

## 6. `scripts/health_server.py`

- **GET** `/health`, `/ready` — JSON status (`version` from `threshold_onset.__version__`, config load check).
- **POST** `/process` — JSON body: `text` (required), optional `return_model_state`, `include_phase10_metrics`, `max_input_length`, `timeout_seconds`, `silent`.
- **Port:** `HEALTH_PORT` env (default 8080).
- **Body size limit:** `DEFAULT_BODY_LIMIT` (2_000_000 bytes) — see script.
- **Response header:** `X-Trace-Id` aligned with `ProcessResult.trace_id` where implemented.

**Docs:** `docs/API.md`, `docs/DEPLOYMENT.md`.

---

## 7. CLI module `python -m threshold_onset`

Exercises used in tests:

- `python -m threshold_onset config` — dumps merged config JSON.
- `python -m threshold_onset health` — health JSON (`status: ok`, `version`, …).

---

## 8. `integration/model` — predict-next

**Contract:** `docs/MODEL_CONTRACT.md`.

**Python API:**

- `evaluate(state, config) -> ModelResult` — read-only accuracy.
- `evaluate_with_learning(state, config) -> ModelResult` — learning rule on **copy** of path scores.
- `ModelConfig.from_project()` — reads `config/default.json` → `["model"]` (`learning_rate`, `prediction_method` / `prediction_methods`).

**Helpers:** `integration/model/contract.py` — `model_state_from_pipeline()`, `path_scores_copy()`.

**README:** `integration/model/README.md`.

---

## 9. SanTEK (`integration/model/santek_base.py`)

**Training / model JSON:**

- Single-file schema with optional `meta.checkpoint` and optional **`meta.phase10_training_summary`** when accumulation is enabled.

**Checkpoints:**

- Background writer thread pool so training is not blocked (`_schedule_training_checkpoint`).
- **`SANTEK_DISABLE_CHECKPOINT=1`** — skip checkpoint writes.
- **`SANTEK_CHECKPOINT_SYNC=1`** — write checkpoints on main thread (debug).
- **`SANTEK_CHECKPOINT_PRETTY=1`** — indented JSON for sync checkpoints.

**Phase 10 inside SanTEK:**

- Workers can compute **merged** Phase 10 across tokenizer methods for one text when **`SANTEK_PHASE10_TRAINING_SUMMARY=1`**; parent merges rows into final `meta.phase10_training_summary`.
- **`SANTEK_PHASE10_MERGED_DEBUG=1`** — DEBUG logs for merged Phase 10 per worker.

**Tokenizers / pipeline:**

- **`SANTEK_INCLUDE_BYTE=1`** — include `byte` tokenizer in default method list (otherwise methods may omit byte for speed).
- **`SANTEK_TRAIN_FAST`** — defaults to **on** in code; when off, `_training_fast_env_overrides()` does not inject skips. **Fast mode display** also treats `PHASE1_SKIP_DISTANCES` / `PHASE3_SKIP_PATH_LENGTHS` as signals (see `fast_mode_active` in `santek_train`).
- **`PHASE1_SKIP_DISTANCES`**, **`PHASE3_SKIP_PATH_LENGTHS`** — read by the pipeline when set; SanTEK’s `_training_fast_env_overrides` sets both to `1` if unset while `SANTEK_TRAIN_FAST` is enabled.
- **`SANTEK_PIPELINE_VERBOSE=1`** — verbose pipeline logging during training.

**Pipeline Phase 10 on each method’s state:**

- When training requests per-method `model_state` with pipeline `include_phase10_metrics`, each method’s state can carry its own `phase10_metrics` (see `santek_train` docstring block around env flags).

---

## 10. Root `santek_base_model.py`

- Thin CLI / UX layer over **`integration.model`** (`santek_train`, `santek_generate`, `load_santek_model`, `save_santek_model`, …).
- Trains using project **`config/default.json`** (corpus paths, URLs, `santek_base_model` section).
- Passes through to integrated SanTEK implementation (paths, checkpoints, optional Phase 10 meta per §9).

---

## 11. Semantic layer wiring

**`threshold_onset.semantic.phase5.consequence_field.ConsequenceFieldEngine`**

- New optional ctor arg: **`phase10_metrics: Optional[Dict[str, Any]]`**.
- On **`save()`**, metadata may include `phase10_metrics` **only as provenance** — **no** change to rollouts, vectors, or consequence math.

**Scripts / examples:**

- **`run_semantic_discovery.py`** — runs pipeline first, builds `model_state`, computes `phase10_jsonable_from_model_state`; passes into engine; **`SEMANTIC_LOG_PHASE10=1`** logs one Phase 10 summary line to stderr.
- **`threshold_onset/semantic/example_complete_workflow.py`** — same pattern (pipeline → `phase10_snap` → `phase10_metrics=` on save).

**`integration/fluency_text_generator.py`** — passes Phase 10 JSON from `model_state` when building semantic artifacts (when available).

**`threshold_onset/semantic/README.md`** — updated for Phase 10 provenance story.

---

## 12. Other integration scripts

| Script | Role |
|--------|------|
| `integration/model_predict_next.py` | CLI: `--phase10` prints Phase 10 summary from `model_state`. |
| `integration/structural_prediction_loop.py` | Uses `return_model_state=True`; optional Phase 10 via `run_phase10_from_model_state`. |

---

## 13. Identity-conditioned layer (unnumbered)

**Path:** `threshold_onset/identity_conditioned/`

- **`IdentityConditionedAccumulator`** — counts **`(source_id, content_id, outcome_key)`**; `to_jsonable()` / `from_jsonable()`.
- **Design:** `docs/IDENTITY_CONDITIONED_CONTINUATION.md` (empirical structure, not baked “halo”).
- **Not** connected to the main pipeline automatically — callers **`record()`** when handles exist.

**Tests:** `threshold_onset/identity_conditioned/tests/test_accumulator.py`.

---

## 14. `config/default.json` (relevant keys)

Under **`pipeline`:**

- `include_phase10_metrics` (bool)
- `phase10_cross_check_phase3` (bool)

Also documents **`santek_base_model`** (corpus file / URLs), **`model`** (learning / prediction), **`corpus`** (`state_path`, etc.) — used by training and corpus tooling.

---

## 15. Documentation set

| File | Purpose |
|------|---------|
| `docs/CANONICAL_PHASE_MAP.md` | Single map: structural 0–4 + **10** vs semantic 5–9; identity-conditioned row; removed shim note. |
| `docs/IDENTITY_CONDITIONED_CONTINUATION.md` | Design + reconciliation table (narrative “Phase 5–6” vs repo paths). |
| `docs/PHASE_STATUS_CANONICAL.md` | Phase 10 called out as read-only analytics layer (plus link to map). |
| `docs/MODEL_CONTRACT.md` | `ModelState` + optional `phase10_metrics`. |
| `docs/API.md` | `process`, `ProcessResult`, REST summary. |
| `docs/DEPLOYMENT.md` | Health server, body flags. |
| `docs/EXECUTION.md`, `docs/EXECUTABLES.md` | Run commands and env patterns. |
| `threshold_onset/phase10/README.md` | Phase 10 usage, multi-method merge, config hooks. |
| `README.md` | Env var table (`PIPELINE_PHASE10_*`, `SEMANTIC_LOG_PHASE10`, `SANTEK_PHASE10_*`, etc.), tree entries for `phase10/` and `identity_conditioned/`. |

---

## 16. Removed duplicate “Phase 5”

- Deleted **`threshold_onset/phase5/`** (shim). **Migration:** `import threshold_onset.phase10` instead of `threshold_onset.phase5`.

---

## 17. Test matrix

**`tests/` (repo root)**

| File | What it covers |
|------|----------------|
| `test_api.py` | `process()`, validation, `to_dict()`, `trace_id`, **`return_model_state` + `include_phase10_metrics`**, `-m threshold_onset config/health`, **slow** `test_rest_process` (spawns `health_server.py`). |
| `test_model_api.py` | `model_state_from_pipeline`, `evaluate` / `evaluate_with_learning`, real pipeline state, learning copy semantics, `ModelConfig`, **Phase 10 absent by default**, **present when** `include_phase10_metrics=True`. |
| `test_run_complete_async.py` | `async_run` with and without `model_state`. |
| `test_santek_phase10_meta_optional.py` | **Slow / heavy** — run with **`RUN_SANTEK_PHASE10_META_TEST=1`**; asserts `meta.phase10_training_summary` on written JSON when env enables it. |
| `test_phase3_convergence.py`, `test_phase4_freeze.py`, `test_corpus_state.py`, `test_runtime_executor.py` | Broader project tests (not Phase-10-specific but part of full suite). |

**Package tests**

- `threshold_onset/phase10/tests/test_phase10.py`
- `threshold_onset/identity_conditioned/tests/test_accumulator.py`

---

## 18. Gaps / intentional non-goals (so far)

- **Identity-conditioned** accumulator has **no** automatic ingestion from `run_complete` or SanTEK — you must call **`record()`** with stable ids.
- **Semantic rollouts** do **not** consume Phase 10 for scoring — only **metadata** on save.
- **REST** test is marked **slow**; default CI may skip it unless you run `-m slow` or similar.

---

## Related docs (short)

- Phase numbering: `docs/CANONICAL_PHASE_MAP.md`
- Source × content: `docs/IDENTITY_CONDITIONED_CONTINUATION.md`
- API: `docs/API.md`
- Model JSON / state: `docs/MODEL_CONTRACT.md`
