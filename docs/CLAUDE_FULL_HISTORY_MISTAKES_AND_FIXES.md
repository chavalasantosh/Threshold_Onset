# THRESHOLD_ONSET — Full History: Every Mistake, Every Fix, Everything Developed

**Use with:** `docs/CLAUDE_HANDOFF_EVERYTHING_IN_DETAIL.md` (current state, OPS, how to run).  
**This file:** Everything that happened — version history, every documented mistake, every fix, and what was built. So you can tell Claude (or anyone) the full story.

---

## 1. Version and Release History

- **v0.1.0 (2024-01-12):** Initial development snapshot; core phases; basic docs.
- **v1.0.0 (2024-01-13):** Phases 0–4 frozen. Phase 0 (action variants, residue, trace). Phase 1 (boundary, cluster, distance). Phase 2 (identity hashes, persistence). Phase 3 (graph, relations, convergence). Phase 4 (symbol aliasing). Tests: Phase 3 convergence, Phase 4 freeze. SanTOK integration. PROJECT_FREEZE.md.
- **v1.1.0 (2025-02-06):** Phases 5–9 (semantic) and structural decoder frozen. Integration scripts frozen (run_all, validate_pipeline, stress_test, fluency_text_generator, test_decoder). PROJECT_FREEZE.md, COMPLETE_PROJECT_DOCUMENTATION, CONTRIBUTING updated.
- **v1.2.0 (2026-02-14):** Enterprise upgrade: config (config/default.json, loader, env overrides), CLI (threshold-onset: run, check, suite, validate, benchmark, config, health), API (threshold_onset.api.process, ProcessResult), REST (scripts/health_server.py POST /process), Docker/docker-compose, logging, exceptions (ThresholdOnsetError, ConfigError, PipelineError, ValidationError), docs (API.md, DEPLOYMENT.md, RUNBOOK.md, ENTERPRISE_ROADMAP.md), input length limits, ValidationError.

**After v1.2.0 (recent work):** Model API (integration/model/), run_complete return_model_state, main.py --check via run_user_result fix, run_all_and_save / run_and_save scripts, semantic scripts fixed to run pipeline first, paper numbers corrected, test_rest_process marked slow + 2.5s wait, NEXT_LAYER_DESIGN.md, GAP_TO_MODEL_ROADMAP.md, MODEL_CONTRACT.md.

---

## 2. Phase 0 — Mistakes and Fixes

**Source:** `docs/history/WORK_LOG.md` (2026-01-12).

**Mistake 1 — Trace as labels (Phase 0 violation)**  
- **Wrong:** Traces were strings like "trace1", "trace2". Strings = symbols = meaning. Phase 0 forbids symbols.  
- **Fix:** Traces changed to structureless floats: `lambda: random.random()`. No names, no labels.

**Mistake 2 — Showing trace values (still leaky)**  
- **Wrong:** Even with float residues, the code displayed trace values. Reader could see patterns and classify — not opaque.  
- **Fix:** Output shows only aggregate statistics (count, unique residues, collision rate). Trace values never displayed. Terminology: "traces" → "residues"; "Residue statistics (opaque, un-nameable)".

**Principle:** A Phase 0 trace must be un-nameable. If you can name it or see the value or classify by eye, Phase 0 has collapsed.

---

## 3. Phase 1 — Prompt Mistakes and Fixes

**Source:** `docs/history/CORRECTIONS_APPLIED.md` (2026-01-13).

**Mistake 1 — "Cluster size distribution"**  
- **Wrong:** "Distribution" implies interpretation.  
- **Fix:** "Cluster size counts (unordered, no distribution interpretation)" and "No distribution interpretation" prohibition.

**Mistake 2 — Thresholds not constrained**  
- **Wrong:** No explicit rule that thresholds must be fixed.  
- **Fix:** "Thresholds must be FIXED, EXTERNAL, and NON-ADAPTIVE"; "No learning, tuning, or optimization allowed in Phase 1"; forbidden: adaptive thresholds, learning, tuning, optimization.

**Mistake 3 — Pattern detection too vague**  
- **Wrong:** "Pattern detection" could allow abstraction.  
- **Fix:** "Pattern detection limited to EXACT EQUALITY or FIXED-WINDOW comparison"; "No abstraction, compression, or symbolic patterning allowed."

**Mistake 4 — Real-time logs risk**  
- **Wrong:** "Displays Phase 1 outputs" could lead to stepwise narration.  
- **Fix:** "Displays FINAL Phase 1 outputs only (no stepwise or temporal logs)"; "No real-time logs, stepwise narration, or temporal displays."

**Phase 0 doc fix:** Residue return wording → "Opaque residue list (internal handoff to Phase 1 only; not to be inspected or displayed)" in PHASE0_FINAL_VERIFICATION.md.

---

## 4. Phase 2/3 Gates — Historical Issues

**Source:** `docs/PHASE_GATES_EXPLANATION.md`.

- **Phase 2 gate:** Needs persistence indicators (repetition_count > 0 or survival_count > 0). Before "finite" action variants, gate failed (no persistence). With finite actions, gate passes.
- **Phase 3 gate:** Needs Phase 2 non-None, persistent identities, persistent relations, stability ratio ≥ MIN_STABILITY_RATIO (e.g. 0.6). Before normalization fix, stability ratio too low. After fix: 100% pass, stability ratio 1.0000, Phase 3 frozen.

---

## 5. Semantic (Phases 5–9) — Hidden Imports and Engineering Bugs

**Source:** `threshold_onset/semantic/CORRECTIONS_APPLIED.md` (2025-01-13).

**4 Hidden Imports (design biases):**

1. **Single rollout policy** — Only "maximize continuation options" hard-baked a worldview. **Fix:** Multiple probe policies (greedy, stochastic top-k, pressure-minimizing, novelty-seeking); consequence vectors as expectation over policies or per-policy.
2. **Uniform entropy** — `entropy = log(out_degree)` assumed uniform. **Fix:** Empirical entropy from rollout counts; Shannon entropy from transition frequencies.
3. **"Learner" bias** — "No training" claim but learner bias term existed. **Fix:** Rename to "Experience Table"; deterministic update from consequence deltas; or remove for Phase 9 v1.
4. **Hand-chosen cluster count** — sqrt(n/2) and clamp to 12 = human prior. **Fix:** Stability-based cluster selection (k-medoids over k, stability vs complexity).

**5 Engineering Bugs:**

1. **Refusal too narrow** — Only next_identity == current. **Fix:** Observer-based refusal via `ContinuationObserver._check_transition_allowed()`.
2. **Near-refusal circularity** — External topology file caused circularity. **Fix:** Near-refusal from rollout logs (sliding window).
3. **Edge delta not counterfactual** — delta = vector(target) - vector(source). **Fix:** Forced-first-step counterfactual (baseline vs conditioned distribution).
4. **Forbidden pattern logic** — Compared pattern to its own 90th percentile. **Fix:** Global distribution (avg_refusal per role_pair vs global 90th percentile).
5. **Binder not derived** — Binder was default else-clause. **Fix:** Derive from topology (betweenness, participation, edge_delta variance) or use role_id only.

**Also:** Template scoring → prefix-match scoring so templates steer generation.

---

## 6. Validation Crush — Known Gaps

**Source:** `validation_crush/GAPS_AND_FIXES.md`.

**Fixed (2026-02-03):** Phase A/D test logic (primary = Phase 9 refusal; system passes if it refuses); import/encoding errors.

**Gaps still documented (not all fixed):**

- **Gap 1 — Tests don't process inputs:** Tests load existing outputs (e.g. phase2_output.json) instead of running the full pipeline on test inputs. Required: process test input through Phases 0–9, then check metrics. Impact: CRITICAL.
- **Gap 2 — Phase B "cycle all 9" tokenization:** Spec says "cycle all 9" methods. This repo supports only 4 (whitespace, word, character, subword); others → "Unsupported tokenization method." "9" belongs to SanTOK/SanVerse; crush spec may be out of sync.
- **Gap 3 — Phase E 100K+ tokens:** Spec requires 100K+ token context; test only ~9K characters. Not fixed.

---

## 7. Paper vs Reality — Every Claim Wrong and Corrected

- **"9 tokenization streams":** Wrong for this repo. Only 4 methods. **Fix:** Paper says "four methods" and notes SanTOK/SanVerse may offer more.
- **Stress test times:** Paper had 100→0.190s, 500→0.518s, 1000→1.280s, 2000→3.438s, 5000→22.169s. Actual: 100→0.614s, 500→1.593s, 1000→5.397s, 2000→15.957s, 5000→78.279s. **Fix:** Tables and prose updated; "~78 seconds (machine-dependent)."
- **Benchmark total time:** Paper 2.43s. Actual 2.22s. **Fix:** 2.22s.
- **External validation total time:** Paper 0.83s. Actual 0.69s. **Fix:** 0.69s.
- **Model accuracy:** Paper didn't mention; reality 11.76% / 42.86% / 0% by input and learning. Left as honest.

**Still to do in paper:** Author block; Acknowledgments "[To be added.]".

---

## 8. main.py --check and run_user_result — What Was Fixed

**Problem:** `main.py --check "text"` runs `integration/run_user_result.py`. Script must run the pipeline and show only the end-user result (input + generated outputs).

**Current behavior:** run_user_result loads run_complete via importlib (spec_from_file_location, exec_module), sets `sys.modules["run_complete"]` so dataclasses resolve (Python 3.13). Calls `run(return_result=True, return_model_state=False)` with stdout redirected. Then `TUIRenderer(show_tui=True).end_user_result(result)`. No legacy _print_end_user_result path.

---

## 9. Model API and run_complete — What Was Developed

- **run_complete.run(..., return_model_state=True):** `result.model_state` = dict with phase2_metrics, phase3_metrics, phase4_metrics, path_scores, tokens, residue_sequences. Downstream (model API, semantic scripts) use this; no disk JSON.
- **integration/model/:** contract (ModelState, ModelResult, learning rule), config (ModelConfig.from_project(), config/default.json "model"), predict, learning (eta, correct/wrong updates on copy of path_scores), api (evaluate, evaluate_with_learning). See docs/MODEL_CONTRACT.md.
- **integration/model_predict_next.py:** Thin CLI over model API.
- **tests/test_model_api.py:** 6 tests.

---

## 10. Semantic Scripts (14 & 15) — Mistake and Fix

**Mistake:** run_semantic_discovery.py and example_complete_workflow.py had empty phase2_metrics, phase3_metrics, phase4_output, symbol_sequences. They assumed Phase 2–4 would be loaded from JSON on disk. Pipeline runs in-memory and does not write those JSONs. Result: ConsequenceFieldError "[phase5] No identities found in phase4_symbols".

**Fix:** At start of each script: (1) Run pipeline with sample text: `run(text_override=DEFAULT_SAMPLE_TEXT, return_result=True, return_model_state=True)`. (2) If no model_state or no Phase 4 identities, exit with clear error. (3) Extract phase2/3/4 from model_state; build symbol_sequences from residue_sequences (segment hash → identity_mappings → identity_to_symbol). (4) Run Phases 5–9 with that state. No disk JSON.

---

## 11. test_rest_process — Flaky Test Fix

**Issue:** test_rest_process starts health_server on port 19999, waits 1s, then POSTs to /process. Server often not ready → TimeoutError. 88/89 tests pass.

**Fix:** @pytest.mark.slow; sleep 2.5s; register "slow" marker in pyproject.toml. Run without it: `pytest -m 'not slow'`.

---

## 12. Run Scripts — What Was Developed

- **scripts/run_all_and_save.py:** 17 commands → output/runs/YYYYMMDD_HHmmss/NN_name.txt + summary.txt. No PowerShell transcript; clean stdout/stderr only.
- **scripts/run_and_save.py:** Pipeline + model + tests → same folder structure; optional --full, --out.
- **docs/RUN_ALL_COMMANDS.md:** All commands; do not use Start-Transcript; use run scripts for clean output.
- **run_and_save.bat:** Wrapper for run_and_save.py.

---

## 13. Design Docs — What Exists and What They Say

- **docs/NEXT_LAYER_DESIGN.md:** Layer 10 (necessity/self-observation) outside THRESHOLD_ONSET; read-only contract to Phase 4 and layers 0–9.
- **docs/GAP_TO_MODEL_ROADMAP.md:** One objective, one learning rule, one interface, one baseline; note that 9-stream claim is wrong for this repo.
- **docs/MODEL_CONTRACT.md:** Model API contract (inputs, outputs, learning rule, entry points).
- **docs/WHAT_YOU_RAN_AND_WHAT_ELSE_EXISTS.md:** main.py = 10 steps; lists all other runnables.
- **docs/FULL_PROJECT_DOCUMENTATION.md:** Project structure, how to run, config, CLI.
- **docs/EXECUTABLES.md:** Essential vs full list of executables.
- **docs/ENTERPRISE_ROADMAP.md:** Enterprise gap analysis and implementation status.
- **PROJECT_FREEZE.md:** Phases 0–9, decoder, integration FROZEN.

---

## 14. Summary Table — Every Mistake and Fix

| Where | Mistake | Fix |
|-------|---------|-----|
| Phase 0 | Trace = strings (labels) | Floats; no labels |
| Phase 0 | Displaying trace values | Only aggregate stats; values hidden |
| Phase 1 prompt | "Distribution" wording | Counts only; no distribution interpretation |
| Phase 1 prompt | Thresholds unconstrained | Fixed, external, non-adaptive only |
| Phase 1 prompt | Pattern detection vague | Exact equality / fixed-window only |
| Phase 1 prompt | Real-time logs | Final outputs only; no stepwise |
| Phase 2/3 | Gate failures | Action variants; normalization fix |
| Semantic | 4 hidden imports | Multiple policies; empirical entropy; experience table; stability k |
| Semantic | 5 engineering bugs | Observer refusal; rollout logs; counterfactual; global percentile; binder |
| Crush | Phase A/D; imports | Refusal primary; encoding fixed |
| Paper | 9 streams; stress times; 2.43/0.83 | 4 methods; real times; 2.22/0.69 |
| main.py --check | run_user_result path | exec_module; TUIRenderer.end_user_result |
| run_complete | No state for downstream | return_model_state=True; model_state dict |
| Model | No single task/interface | integration/model/ + MODEL_CONTRACT |
| Semantic 14 & 15 | Empty phase2/3/4; disk JSON | Run pipeline first; model_state in memory |
| test_rest_process | 1s → timeout | @pytest.mark.slow; 2.5s; marker |
| Saving output | Start-Transcript messy | run_all_and_save; run_and_save; RUN_ALL_COMMANDS |

---

**End.** Use this together with `CLAUDE_HANDOFF_EVERYTHING_IN_DETAIL.md` to give Claude (or any AI) everything: current state plus full history of what was built, every mistake, and every fix.
