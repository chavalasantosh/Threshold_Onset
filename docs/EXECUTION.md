# How to Run THRESHOLD_ONSET

**Date:** 2026-01-13  
**Status:** Current execution model

---

## Quick Reference

| Command | What it does |
|---------|---------------|
| `threshold-onset run` | Enterprise CLI: run full pipeline (or `python -m threshold_onset run`) |
| `threshold-onset check "text"` | Quick user-facing check |
| `threshold-onset config` | Show current config |
| `python main.py` | Full 10-step suite (decoder, validation, stress, benchmark, baselines, external validation, stability, structural scaling, full pipeline) |
| `python main.py --check "text"` | Quick pipeline check with user-facing output |
| `python main.py --user "text"` | Full suite with your text used in step 10 |
| `python main.py --user` | Interactive: prompts for text, then runs full suite |
| `python run_all.py` | Same as `main.py` (equivalent entry point) |
| `python integration/run_complete.py` | Direct full pipeline (text → structure → text) |
| `python integration/run_complete.py "Your text"` | Same pipeline with custom input |
| `python integration/run_user_result.py "Your text"` | User-facing output (used by `--check`) |
| `main.bat` / `run_all.bat` | Windows batch wrappers |
| `python project_viewer.py` | Runs all 10 steps (same as main.py) |
| `python project_viewer.py --describe` | Print overview only (no execution) |
| `python project_viewer.py --verbose` | Full report with module dump |
| `python project_viewer.py --out FILE` | Write report to file |
| `python project_viewer.py --full --out FILE` | Full source of every .py file (excludes main.py) |
| `python project_viewer.py --json` | Output as JSON |

---

## 10-Step Suite (main.py / run_all.py)

When you run `python main.py` or `python run_all.py`, these steps execute in order:

1. **Decoder test** — `integration/test_decoder.py`
2. **Validation** — `integration/validate_pipeline.py` (7 input types)
3. **Stress test** — `integration/stress_test.py` (scale 100–5000 tokens)
4. **Benchmark** — `integration/benchmark.py` (39 samples)
5. **Baselines** — `integration/baselines.py` (4 methods)
6. **External validation** — `integration/external_validation.py` (136 samples)
7. **Stability mode** — `integration/stability_mode.py` (perturbed runs)
8. **Stability experiments** — `integration/stability_experiments.py` (parameter sweep)
9. **Structural scaling** — `integration/structural_scaling.py` (topology law)
10. **Full pipeline** — `integration/run_complete.py` (text → structure → text)

Each step runs as a subprocess. Pass/fail is reported at the end.

---

## Pipeline Configuration

**Enterprise config (recommended):** Pipeline parameters are loaded from `config/default.json` with environment overrides.

| Parameter | Config key | Env override | Default |
|-----------|------------|--------------|---------|
| `tokenization_method` | `pipeline.tokenization_method` | `THRESHOLD_ONSET_TOKENIZATION` | `"word"` |
| `num_runs` | `pipeline.num_runs` | `THRESHOLD_ONSET_NUM_RUNS` | `3` |
| `log_level` | `pipeline.log_level` | `THRESHOLD_ONSET_LOG_LEVEL` | `"INFO"` |
| `output_dir` | `pipeline.output_dir` | `THRESHOLD_ONSET_OUTPUT_DIR` | `"output"` |

Config file: set `THRESHOLD_ONSET_CONFIG` to override path. See `docs/DEPLOYMENT.md`.

---

## Direct Pipeline Runs

**Full pipeline (default corpus):**
```bash
python integration/run_complete.py
```

**Full pipeline with your text:**
```bash
python integration/run_complete.py "Your text here"
```

**User-facing output (clean, readable):**
```bash
python integration/run_user_result.py "Your text here"
```

---

## Windows

```cmd
set PYTHONIOENCODING=utf-8
python main.py
```

Or use the batch files:
```cmd
main.bat
run_all.bat
```

---

## See Also

- **`docs/EXECUTABLES.md`** — Complete list of all executables (what you can run, what you need to run)
- `QUICK_START.md` — Short run instructions
- `docs/EXECUTION_MODES.md` — Single-run vs multi-run (config in integration scripts)
- `integration/README.md` — Integration module overview
