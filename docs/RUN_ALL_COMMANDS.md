# All Commands — Copy-Paste Reference

**Windows PowerShell:** Use `;` between commands (not `&&`). Set encoding: `$env:PYTHONIOENCODING="utf-8"`

Replace `REPO` with your project folder, e.g. `c:\Users\SCHAVALA\Downloads\codes\THRESHOLD_ONSET - Copy`

---

## 0. Saving output for next analysis

**Do not use Start-Transcript.** That saves a raw PowerShell session (prompts, escape codes, no clean output). Use the scripts below instead.

**One full clean log for handoff (to Cursor or Claude):**
```powershell
cd "REPO"
$env:PYTHONIOENCODING="utf-8"
python scripts/run_full_clean_log.py
```
Creates **one** UTF-8 file: `output/FULL_CLEAN_LOG.txt` (and a timestamped copy in `output/`). No Tee-Object, no console code page — subprocess capture only. Give that file to the next assistant.

**Faster (skip full main.py):**
```powershell
python scripts/run_full_clean_log.py --quick
```
Runs: main.py --check, run_complete, structural_prediction_loop, santek_sle, validate_pipeline, pytest (model + phase4). Same output file.

**Full command list → clean output in one go:**
```powershell
$env:PYTHONIOENCODING="utf-8"
python scripts/run_all_and_save.py
```
Creates `output/runs/YYYYMMDD_HHmmss/` with one file per command (01_main.txt through 17_validate_pipeline.txt) plus summary.txt. Each file = that command’s real stdout/stderr only.

**Save stdout to a file (overwrite):**
```powershell
python main.py > output.txt
```

**Save both stdout and stderr to one file:**
```powershell
python main.py *> output.txt
```

**Save and still see output on screen (tee):**
```powershell
python main.py 2>&1 | Tee-Object -FilePath output.txt
```

**Append to a file (don't overwrite):**
```powershell
python main.py *>> output.txt
```

**Save to a timestamped file (good for runs over time):**
```powershell
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
python main.py *> "output_$ts.txt"
```

**Run essentials and save each to a separate file (recommended — use the script):**
```powershell
python scripts/run_and_save.py
```
Output goes to `output/runs/YYYYMMDD_HHmmss/` (01_check.txt, 02_model_no_learn.txt, 03_model_learn.txt, 04_model_tests.txt, summary.txt). Optional: `--full` adds full 10-step suite; `--out my_dir` uses a custom folder.

Or double-click **run_and_save.bat** (same as above).

**Execution log / Tee-Object notes:**
- If you use `Tee-Object` or `*> execution_log.txt`, the log may show **mojibake** (e.g. `ΓöîΓöÇ`) when Python prints UTF-8 and the console code page is not UTF-8. For clean UTF-8 logs, use `run_all_and_save.py` or run with `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` before the command.
- Python’s `logging` (and some print) writes to **stderr**. PowerShell can show those lines as `python : ... RemoteException`. That is stderr, not necessarily a failing exit code.
- **Structural Prediction Loop** and **SanTEK-SLE** need at least two identities so there are transitions to predict. If the input tokenizes to a single repeated token (e.g. one unique word), the pipeline yields one identity and **0 path scores** → the loop exits with a clear message. Use longer or more varied text.

**Run full suite and save everything to one log:**
```powershell
cd "REPO"
$env:PYTHONIOENCODING="utf-8"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
python main.py *> "suite_$ts.log"
Write-Host "Saved to suite_$ts.log"
```

---

## 1. Go to project and set encoding (do this first)

```powershell
cd "REPO"
$env:PYTHONIOENCODING="utf-8"
```

---

## 2. Full validation suite (10 steps)

```powershell
python main.py
```

Quick pipeline with your text only:

```powershell
python main.py --check "Action before knowledge."
```

---

## 3. Pipeline only (no suite)

```powershell
python integration/run_complete.py "Your text here"
```

Minimal output (no TUI):

```powershell
python integration/run_complete.py --no-tui "Your text here"
```

---

## 4. Model (predict-next accuracy)

No learning:

```powershell
python integration/model_predict_next.py "Action before knowledge. Function stabilizes."
```

With learning:

```powershell
python integration/model_predict_next.py --learn "Action before knowledge. Function stabilizes."
```

With custom learning rate:

```powershell
python integration/model_predict_next.py --learn --eta 0.1 "Your text"
```

---

## 5. Tests

All tests:

```powershell
python -m pytest tests/ threshold_onset/semantic/tests/ -v
```

Model API tests only:

```powershell
python -m pytest tests/test_model_api.py -v
```

Phase 4 tests:

```powershell
python -m pytest tests/test_phase4_freeze.py -v
```

Semantic (Phase 5–9) tests:

```powershell
python -m pytest threshold_onset/semantic/tests/ -v
```

---

## 6. Crush validation (phases A–I)

All phases:

```powershell
python validation_crush/crush_protocol.py --all
```

Single phase (A, B, C, … I):

```powershell
python validation_crush/crush_protocol.py --phase A
```

---

## 7. Semantic discovery (Phases 5–9)

```powershell
python run_semantic_discovery.py
```

Example workflow:

```powershell
python threshold_onset/semantic/example_complete_workflow.py
```

---

## 8. Individual suite steps (run one at a time)

```powershell
python integration/test_decoder.py
python integration/validate_pipeline.py
python integration/stress_test.py
python integration/benchmark.py
python integration/baselines.py
python integration/external_validation.py
python integration/stability_mode.py
python integration/stability_experiments.py
python integration/structural_scaling.py
python integration/run_complete.py "Your text"
```

---

## 9. Training and analysis

```powershell
python integration/train.py --epochs 50 --interval 5
python integration/run_corpus_scale.py
python integration/run_corpus_stress.py
python integration/escape_topology.py
python integration/topology_clusters.py
python integration/scoring.py
python integration/refusal_signatures.py
python integration/observe_refusals.py
python integration/compare_topologies.py
```

---

## 10. Other scripts

```powershell
python integration/generate.py
python integration/unified_system.py
python integration/test_invariant.py
python integration/test_permuted.py
python integration/test_continuation.py
python integration/near_refusal_observer.py
python integration/main_complete.py
python integration/main_end_to_end.py
python scripts/health_server.py
python project_viewer.py --describe
python run_and_log.py
python run_and_log.py --quick
```

---

## 11. CLI (after pip install -e .)

```powershell
pip install -e .
threshold-onset run "Your text"
threshold-onset check "Your text"
threshold-onset suite
threshold-onset config
threshold-onset health
```

---

## 12. One block to run the essentials (PowerShell)

```powershell
cd "REPO"
$env:PYTHONIOENCODING="utf-8"
python main.py --check "Action before knowledge."
python integration/model_predict_next.py "Action before knowledge."
python integration/model_predict_next.py --learn "Action before knowledge."
python -m pytest tests/test_model_api.py -v
```

Replace REPO with your full path. This runs: quick pipeline check, model accuracy without learning, model accuracy with learning, model API tests.

**To save this block's output to one file:** add `*> essentials.txt` after the last line, or run each line as `python ... *> step1.txt` etc. See **Section 0** for more ways to save output for analysis.
