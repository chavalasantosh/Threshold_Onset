# THRESHOLD_ONSET — Full Context for Claude

**Purpose:** Give another Claude (or any AI) **everything**: what this repo is, what runs, what passed/failed, **every mistake that was made and fixed**, and **the full development history** so nothing is lost. Read this first before making changes.

**Quick reference:** Sections 1–9 = current state, OPS, how to run. **Full history (every mistake, every fix, everything developed):** See **`docs/CLAUDE_FULL_HISTORY_MISTAKES_AND_FIXES.md`** — give Claude both files so it has everything.

---

## 1. What This Project Is

**THRESHOLD_ONSET** is a **structure-first** system for text: identity and relations are **induced from action and repetition**, not assumed. It is not a language model; it discovers and enforces **structural invariants** (e.g. no self-transitions) from tokens → residues → identities → relations → symbols.

- **Four axioms:** (1) Action before knowledge; (2) Identity is earned by recurrence; (3) Constraint bounds generation; (4) Structural inversion (decoder: symbol → identity → residue → token).
- **9-phase pipeline:** Phases 0–4 = structure emergence (residue, cluster, identity, relation, symbol); Phases 5–9 = semantic discovery (consequence field, meaning, roles, constraints, fluency). Phase $i$ may not use tools from phase $j$ for $j > i$.
- **Two modes:** Deterministic (reproducibility) and stability (identity under Bernoulli perturbation; mean-field boundary $p^* = 1 - \sqrt{\theta/K}$).
- **Papers:** LaTeX in `paper/` (NeurIPS-style `main.tex`, longer `main_paperbanana_style.tex`). Numbers in the paper were corrected to match actual runs (stress table, benchmark 2.22s, external 0.69s, tokenization = 4 methods).

---

## 2. Repo Layout (What Lives Where)

| Path | Purpose |
|------|--------|
| `main.py` | Entry point: full suite or `--check "text"` for quick pipeline. |
| `integration/run_complete.py` | **Core pipeline**: runs Phases 0–4, generation, decoder. `run(..., return_model_state=True)` returns `PipelineResult` with `model_state` (phase2/3/4, path_scores, tokens, residue_sequences). |
| `integration/model/` | **Model API**: predict-next-identity over pipeline state. `evaluate()`, `evaluate_with_learning()`, `ModelConfig`, `ModelResult`. Contract in `docs/MODEL_CONTRACT.md`. |
| `integration/model_predict_next.py` | CLI over model API (no business logic in script). |
| `threshold_onset/phase0` … `phase4/` | Frozen structure phases (residue, cluster, identity, relation, symbol). |
| `threshold_onset/semantic/` | Phases 5–9: consequence field, meaning, roles, constraints, fluency. |
| `run_semantic_discovery.py` | Runs pipeline in-memory first, then Phases 5–9 (no disk JSON). |
| `threshold_onset/semantic/example_complete_workflow.py` | Same idea: pipeline first, then semantic workflow. |
| `integration/continuation_observer.py` | Records refusals (e.g. self-transition attempts); used by semantic and generation. |
| `validation_crush/` | Adversarial phase validation (phases A–I). |
| `scripts/run_all_and_save.py` | Runs 17 commands, saves each stdout/stderr to `output/runs/YYYYMMDD_HHmmss/` (01_main.txt … 17_validate_pipeline.txt, summary.txt). |
| `scripts/run_and_save.py` | Shorter run: pipeline + model + tests, output in same folder structure. |
| `config/default.json` | Default config; includes `model` section (eta, etc.). |
| `paper/` | LaTeX: `main.tex`, `appendix.tex`, `main_paperbanana_style.tex`. |
| `docs/` | Design and runbooks: `RUN_ALL_COMMANDS.md`, `MODEL_CONTRACT.md`, `GAP_TO_MODEL_ROADMAP.md`, `NEXT_LAYER_DESIGN.md`, etc. |

**Tokenization:** This repo supports **four** methods only: whitespace, word, character, subword (santok or whitespace fallback). The “9 tokenization streams” claim belongs to SanTOK/SanVerse, not this repo.

---

## 3. What Actually Runs — The 17 Commands (OPS)

The canonical run is captured in `scripts/run_all_and_save.py`. Each command writes to a numbered file; a **summary.txt** lists exit codes.

### 3.1 Commands (in order)

| File | What it runs | Verdict |
|------|--------------|--------|
| 01_main.txt | `python main.py` — full pipeline + validation + stress + benchmark 39/39 + baselines + external 136/136 + stability | **PASS** (exit 0) |
| 02_check.txt | `main.py --check "chinni gunde lo anni asala."` — full pipeline, 5 tokens, 3 outputs | **PASS** |
| 03_run_complete_empty.txt | `run_complete.py ""` — empty input | **exit 1** (intended: guard “Empty input — provide text or a file path”) |
| 04_run_complete_notui.txt | `run_complete.py --no-tui "inka yenni dhachi navoo dhanni lona"` | **PASS** |
| 05_model.txt | `model_predict_next.py "Action before knowledge. ..."` — no learning, accuracy e.g. 11.76% | **PASS** |
| 06_model_learn.txt | `model_predict_next.py --learn "oohaa lo illa telave ala."` — learning ON, accuracy e.g. 42.86% | **PASS** |
| 07_model_learn_eta.txt | `model_predict_next.py --learn --eta 0.1 "vinthalanni ..."` — learning ON, e.g. 0% (honest) | **PASS** |
| 08_pytest_all.txt | `pytest tests/ threshold_onset/semantic/tests/ -v` | **exit 1** (flaky: `test_rest_process` timeout) |
| 09_pytest_model.txt | `pytest tests/test_model_api.py -v` — 6/6 model API tests | **PASS** |
| 10_pytest_phase4.txt | `pytest tests/test_phase4_freeze.py -v` — 4/4 Phase 4 tests | **PASS** |
| 11_pytest_semantic.txt | `pytest threshold_onset/semantic/tests/ -v` — 66/66 semantic tests | **PASS** |
| 12_crush_all.txt | `validation_crush/crush_protocol.py --all` — phases A–I | **PASS** |
| 13_crush_A.txt | `crush_protocol.py --phase A` | **PASS** |
| 14_semantic_discovery.txt | `python run_semantic_discovery.py` | **PASS** after fix (runs pipeline first, then 5–9) |
| 15_semantic_workflow.txt | `python threshold_onset/semantic/example_complete_workflow.py` | **PASS** after fix (same) |
| 16_test_decoder.txt | `integration/test_decoder.py` | **PASS** |
| 17_validate_pipeline.txt | `integration/validate_pipeline.py` — 7-type validation | **PASS** |

### 3.2 The Four “Failures” (and what they mean)

1. **03 — exit 1 (empty input)**  
   Not a bug. Pipeline correctly rejects empty input with a clear message. Leave as-is.

2. **08 — exit 1 (pytest all)**  
   **Cause:** `test_rest_process` in `tests/test_api.py` starts `scripts/health_server.py` on port 19999, waits 1s, then POSTs to `/process`. The server often isn’t ready in 1s → timeout. **Fix applied:** Test marked `@pytest.mark.slow`, startup wait increased to 2.5s. To run tests without it: `pytest -m 'not slow'`.

3. **14 — run_semantic_discovery.py (pre-fix)**  
   **Cause:** Script expected Phase 2–4 data from disk JSON; pipeline runs in-memory only → `ConsequenceFieldError: [phase5] No identities found in phase4_symbols`. **Fix applied:** At start, script runs `integration.run_complete.run(sample_text, return_model_state=True)`, then uses `model_state` (phase2/3/4, residue_sequences) to build symbol_sequences and runs Phases 5–9. No disk JSON needed.

4. **15 — example_complete_workflow.py (pre-fix)**  
   Same as 14. Same fix: run pipeline first, pass phase2/3/4 and symbol_sequences from `model_state` in memory.

---

## 4. Paper vs Reality (What Was Corrected)

- **Stress test table:** Replaced with measured times: 100→0.614s, 500→1.593s, 1000→5.397s, 2000→15.957s, 5000→78.279s (all Success). In both `paper/main.tex` and `paper/main_paperbanana_style.tex`.
- **Benchmark total time:** 2.22s (not 2.43s).
- **External validation total time:** 0.69s (not 0.83s).
- **Tokenization:** Removed “9 streams”; stated that this repo supports **4** methods (whitespace, word, character, subword); SanTOK/SanVerse may offer more elsewhere.
- **Stress prose:** “~78 seconds (machine-dependent)” for 5000 tokens.
- **Placeholders still to fill:** Author block (names, affiliations, email), Acknowledgments (“[To be added.]”) in `main.tex` / `main_paperbanana_style.tex`.

---

## 5. Key Technical Details

### 5.1 Pipeline state for downstream use

- `run_complete.run(text_override=..., return_result=True, return_model_state=True)` returns `PipelineResult`.
- `result.model_state` is a dict: `phase2_metrics`, `phase3_metrics`, `phase4_metrics`, `path_scores`, `tokens`, `residue_sequences`. The model API and the semantic scripts consume this; they do **not** read Phase 2–4 from JSON files.

### 5.2 Symbol sequences from model_state

- Phase 2 has `identity_mappings`: segment_hash → identity_hash (segment = tuple of two consecutive residues, hashed with same rule as `threshold_onset/phase2/identity.py`).
- Phase 4 has `identity_to_symbol` (identity_hash → int).
- To build `symbol_sequences` (list of lists of symbol indices) from `residue_sequences`: for each run, for each consecutive pair `(r_i, r_{i+1})`, compute segment hash, look up identity_hash, then symbol; append to sequence. Implemented in `run_semantic_discovery.py` and `example_complete_workflow.py` via `_segment_hash()` and `_symbol_sequences_from_model_state()`.

### 5.3 Model API

- **Input:** `ModelState` = same shape as `result.model_state` (phase2/3/4, path_scores, tokens, residue_sequences).
- **Output:** `ModelResult`: accuracy, total_predictions, correct_predictions, optional updated_path_scores when learning is on.
- **Learning rule:** On correct prediction: `path_scores[(current, actual_next)] += eta`. On wrong: decrement predicted, increment actual. Updates on a **copy** of path_scores only.
- Config: `config/default.json` has a `model` section; `ModelConfig.from_project()` loads it.

### 5.4 Semantic scripts (14 & 15)

- Both now: (1) Run pipeline with a fixed sample text (e.g. Telugu sentences). (2) If `model_state` is missing or has no Phase 4 identities, exit with a clear error. (3) Build symbol_sequences from residue_sequences + phase2/4. (4) Run ConsequenceFieldEngine → MeaningDiscovery → RoleEmergence → ConstraintDiscovery → FluencyGenerator with that state. No dependency on pre-written JSON.

---

## 6. How to Run Things (for Claude or a human)

- **Encoding (Windows):** `$env:PYTHONIOENCODING="utf-8"` before running Python if you care about non-ASCII output.
- **Save all 17 outputs cleanly:**  
  `python scripts/run_all_and_save.py`  
  Output: `output/runs/YYYYMMDD_HHmmss/` with 01_main.txt … 17_validate_pipeline.txt and summary.txt. Do **not** use PowerShell Start-Transcript for “clean” logs; use this script.
- **Quick pipeline check:**  
  `python main.py --check "Your text here"`
- **Pipeline only (no TUI):**  
  `python integration/run_complete.py --no-tui "Your text"`
- **Model (no learning / with learning):**  
  `python integration/model_predict_next.py "text"`  
  `python integration/model_predict_next.py --learn "text"`
- **Tests:**  
  All: `python -m pytest tests/ threshold_onset/semantic/tests/ -v`  
  Skip slow (e.g. health server): `python -m pytest -m 'not slow' tests/ threshold_onset/semantic/tests/ -v`  
  Model API only: `python -m pytest tests/test_model_api.py -v`  
  Phase 4: `python -m pytest tests/test_phase4_freeze.py -v`  
  Semantic: `python -m pytest threshold_onset/semantic/tests/ -v`
- **Crush:**  
  `python validation_crush/crush_protocol.py --all`
- **Semantic discovery:**  
  `python run_semantic_discovery.py`  
  `python threshold_onset/semantic/example_complete_workflow.py`
- Full command reference: **`docs/RUN_ALL_COMMANDS.md`**.

---

## 7. Important Docs (Read When Relevant)

| Doc | When to use |
|-----|-------------|
| `docs/RUN_ALL_COMMANDS.md` | Copy-paste commands, saving output, PowerShell-safe. |
| `docs/MODEL_CONTRACT.md` | Model API inputs/outputs, learning rule, entry points. |
| `docs/GAP_TO_MODEL_ROADMAP.md` | Turning the research architecture into a single-objective “model” (one task, one learning rule, one interface, one evaluation). |
| `docs/NEXT_LAYER_DESIGN.md` | Layer 10 (necessity/self-observation) design; read-only contract to Phase 4 and layers 0–9; implementation outside this repo. |
| `paper/README.md` | Paper structure, compile instructions (pdflatex main.tex; appendix input in main). |
| `integration/README.md` | Integration scripts overview. |

---

## 8. Conventions and Gotchas

- **No disk Phase 2–4 for semantic:** Any script that runs Phases 5–9 must get Phase 2–4 from **running the pipeline** (in-memory or via `model_state`). Do not assume JSON files on disk.
- **Empty input:** Exiting with code 1 and a clear “Empty input” message is correct behavior; do not treat as a bug.
- **test_rest_process:** Slow and flaky; marked `@pytest.mark.slow`; wait 2.5s for server. Use `-m 'not slow'` in CI if needed.
- **Papers:** Both `main.tex` and `main_paperbanana_style.tex` were updated to match actual numbers and 4-method tokenization; author/ack placeholders still to be filled.
- **PyPI / package name:** `threshold-onset`; repo: https://github.com/chavalasantosh/THRESHOLDONSET.

---

## 9. One-Paragraph Summary for Claude

THRESHOLD_ONSET is a structure-first pipeline: tokens → residues → identities → relations → symbols (Phases 0–4), then optional semantic Phases 5–9. Identity is induced by recurrence; generation is constraint-bound (no self-transitions). The repo runs 17 commands; 13 pass fully, 1 is an intentional empty-input guard (exit 1), 1 is a flaky server test (now marked slow, 2.5s wait), and 2 semantic scripts were fixed to run the pipeline in-memory first instead of reading missing Phase 2–4 JSON. The paper’s stress table, benchmark (2.22s), and external (0.69s) times and tokenization (4 methods) are corrected. Model API in `integration/model/` does predict-next-identity with optional learning over `path_scores`. Use `scripts/run_all_and_save.py` for clean saved output; see `docs/RUN_ALL_COMMANDS.md` for all commands.
