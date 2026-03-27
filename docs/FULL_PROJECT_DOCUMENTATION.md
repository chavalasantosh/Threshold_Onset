# THRESHOLD_ONSET — Full Project Documentation

**Purpose:** Single reference for the entire project: what it is, how to run everything, and where to find details.

**Status:** Project is FROZEN (see root `PROJECT_FREEZE.md`). This doc reflects the codebase as of the current state.

---

## 1. What This Project Is

**THRESHOLD_ONSET** is a foundational system for *structure emergence through action, trace, and repetition* — before symbols, meaning, or interpretation.

- **Tagline:** *Action before knowledge* — कार्य (kārya) happens before ज्ञान (jñāna).
- **Core idea:** Tokenization → Phases 0–4 (structure emergence) → Continuation observation → Escape topology → Clustering → Path scoring → Surface mapping → Text generation. No external embeddings; structure comes from the pipeline.
- **Package:** `threshold-onset` on PyPI; install with `pip install -e .` for the enterprise CLI.
- **Config:** `config/default.json`; overrides via environment (see `docs/DEPLOYMENT.md`).

---

## 2. Project Structure (Relevant Parts)

```
THRESHOLD_ONSET - Copy/
├── config/
│   └── default.json              # Pipeline config (tokenization, num_runs, etc.)
├── integration/                  # Pipeline, validation, benchmarks, analysis (38+ modules)
│   ├── run_complete.py           # Main full pipeline (text → structure → text)
│   ├── run_user_result.py        # User-facing output (used by --check)
│   ├── validate_pipeline.py     # Validation (7 input types)
│   ├── stress_test.py            # Stress test
│   ├── benchmark.py              # Benchmark
│   ├── baselines.py              # Baselines
│   ├── external_validation.py    # External validation
│   ├── train.py                  # Preference learner training
│   ├── main_complete.py          # Alternative main
│   ├── main_end_to_end.py        # End-to-end run
│   └── ...                       # (refusal_signatures, scoring, topology, etc.)
├── threshold_onset/              # Main package
│   ├── __main__.py               # python -m threshold_onset
│   ├── cli.py                    # Enterprise CLI (run, check, suite, health, etc.)
│   ├── api.py                    # Programmatic API (process, ProcessResult)
│   ├── phase0/ ... phase4/       # Structure emergence phases
│   ├── semantic/                 # Phases 5–9 (consequence, meaning, roles, constraints, fluency)
│   ├── core/, config/, tools/    # Logging, config loader, version tools
│   └── universal_input.py        # File/text input handling
├── scripts/
│   └── health_server.py          # HTTP health/process server (port 8080)
├── tests/                        # Root tests (phase3, phase4, api, corpus_state)
├── validation_crush/             # Crush protocol (phases A–I)
├── docs/                         # API.md, DEPLOYMENT.md, EXECUTABLES.md, EXECUTION.md, etc.
├── main.py                       # Full 10-step suite entry point
├── run_all.py                    # Same as main.py
├── run_and_log.py                # Full run with log to file
├── project_viewer.py             # Run 10 steps or report only
├── run_semantic_discovery.py     # Standalone Phases 5–9
├── pyproject.toml                # Package definition, CLI script, Pylint config
└── README.md                     # Quick start, install, CLI summary
```

---

## 3. How to Execute the Full Project

### 3.1 One Command: Full 10-Step Suite

This runs the **entire** validation suite (decoder, validation, stress, benchmark, baselines, external validation, stability, structural scaling, full pipeline):

```bash
# From project root; ensure UTF-8 on Windows if needed
set PYTHONIOENCODING=utf-8
python main.py
```

**Equivalent:**

```bash
python run_all.py
# or
python project_viewer.py
```

Each step runs as a subprocess. Pass/fail is reported at the end.

### 3.2 Quick Check (Single Pipeline Run)

```bash
python main.py --check "Your text here"
# or (after pip install -e .)
threshold-onset check "Your text here"
```

### 3.3 Pipeline Only (No Suite)

```bash
python integration/run_complete.py
# With custom input:
python integration/run_complete.py "Your text here"
```

### 3.4 Enterprise CLI (After `pip install -e .`)

| Command | Purpose |
|---------|---------|
| `threshold-onset run` | Full pipeline (default corpus) |
| `threshold-onset run "text"` | Full pipeline with custom input |
| `threshold-onset check "text"` | Quick user-facing check |
| `threshold-onset suite` | Full 10-step evaluation suite |
| `threshold-onset validate` | Validation only |
| `threshold-onset benchmark` | Benchmark only |
| `threshold-onset config` | Show config (JSON) |
| `threshold-onset health` | Health check (JSON) |

Without install, from project root:

```bash
python -m threshold_onset run
python -m threshold_onset health
```

### 3.5 Log Full Run to File

```bash
python run_and_log.py              # Appends to execution_log.txt
python run_and_log.py --quick      # Check + run_complete only
python run_and_log.py --out FILE   # Custom output file
```

---

## 4. All Executable Entry Points (Reference)

### Root

| Command | Purpose |
|---------|---------|
| `python main.py` | Full 10-step suite |
| `python main.py --check "text"` | Quick pipeline check |
| `python main.py --user "text"` | Full suite with your text in step 10 |
| `python main.py --user` | Interactive text, then full suite |
| `python run_all.py` | Same as main.py |
| `python run_and_log.py` [--quick] [--out FILE] | Run and log |
| `python project_viewer.py` | Run all 10 steps |
| `python project_viewer.py --describe` | Overview only (no run) |
| `python project_viewer.py --verbose` | Full module report |
| `python project_viewer.py --out FILE` | Write report to file |
| `python run_semantic_discovery.py` | Standalone Phases 5–9 |
| `python test_large_context.py` | Large-context test |

### Integration (Pipeline & Analysis)

| Command | Purpose |
|---------|---------|
| `python integration/run_complete.py` ["text"] | Full pipeline |
| `python integration/run_user_result.py "text"` | User-facing output only |
| `python integration/run_user_input.py` | Quick pipeline (benchmark mode) |
| `python integration/validate_pipeline.py` | Validation (7 input types) |
| `python integration/stress_test.py` | Stress test |
| `python integration/benchmark.py` | Benchmark |
| `python integration/baselines.py` | Baselines |
| `python integration/external_validation.py` | External validation |
| `python integration/stability_mode.py` | Stability mode |
| `python integration/stability_experiments.py` | Stability experiments |
| `python integration/structural_scaling.py` | Structural scaling |
| `python integration/run_corpus_scale.py` | Corpus-scale (multiprocessing) |
| `python integration/run_corpus_stress.py` | Corpus stress |
| `python integration/train.py --epochs N --interval N` | Train preference learner |
| `python integration/escape_topology.py` | Escape topology |
| `python integration/topology_clusters.py` | Topology clustering |
| `python integration/refusal_signatures.py` | Refusal signature analysis |
| `python integration/main_complete.py` | Alternative main |
| `python integration/main_end_to_end.py` | End-to-end run |
| `python integration/scoring.py` | Scoring (main) |
| … (see docs/EXECUTABLES.md for full list) | |

### 10-Step Suite (Individual Steps)

| Step | Command |
|------|---------|
| 1 | `python integration/test_decoder.py` |
| 2 | `python integration/validate_pipeline.py` |
| 3 | `python integration/stress_test.py` |
| 4 | `python integration/benchmark.py` |
| 5 | `python integration/baselines.py` |
| 6 | `python integration/external_validation.py` |
| 7 | `python integration/stability_mode.py` |
| 8 | `python integration/stability_experiments.py` |
| 9 | `python integration/structural_scaling.py` |
| 10 | `python integration/run_complete.py` |

### Package & Scripts

| Command | Purpose |
|---------|---------|
| `python -m threshold_onset` | Same as CLI main |
| `python -m threshold_onset run` | Full pipeline |
| `python scripts/health_server.py` | Health/process HTTP server (GET /health, POST /process) |
| `python validation_crush/crush_protocol.py --all` | Crush validation (phases A–I) |
| `python validation_crush/crush_protocol.py --phase A` | Single crush phase |
| `python threshold_onset/semantic/example_complete_workflow.py` | Semantic workflow example |

---

## 5. Tests

| Command | What runs |
|---------|-----------|
| `python -m pytest tests/ threshold_onset/semantic/tests/` | All project + semantic tests |
| `python -m pytest tests/ -v` | Root tests only |
| `python -m pytest tests/test_api.py -v --tb=short` | API integration (CI) |
| `python tests/test_phase3_convergence.py` | Phase 3 convergence (script) |
| `python tests/test_phase4_freeze.py` | Phase 4 freeze (script) |
| `python threshold_onset/semantic/tests/test_integration.py` | Semantic integration (unittest) |
| `python threshold_onset/semantic/tests/test_phase5.py` … `test_phase9.py` | Phase 5–9 tests (unittest) |

---

## 6. Configuration

- **File:** `config/default.json` (pipeline section: tokenization_method, num_runs, etc.).
- **Env:** e.g. `THRESHOLD_ONSET_CONFIG`, `THRESHOLD_ONSET_TOKENIZATION`, `THRESHOLD_ONSET_NUM_RUNS`. See `docs/DEPLOYMENT.md`.

---

## 7. Programmatic API

```python
from threshold_onset.api import process, ProcessResult

result = process("Your input text")
# result.success, result.generated_outputs, result.token_count, etc.
```

Full reference: **docs/API.md**.

---

## 8. Existing Documentation (Pointers)

| Document | Content |
|----------|---------|
| **README.md** (root) | Quick start, install, CLI, project status |
| **docs/EXECUTABLES.md** | All runnables with short descriptions |
| **docs/EXECUTION.md** | How to run, 10-step suite, config table |
| **docs/API.md** | Programmatic API reference |
| **docs/DEPLOYMENT.md** | Docker, env vars, production |
| **docs/architecture/** | Architecture notes |
| **integration/README.md** | Integration module overview |
| **threshold_onset/semantic/README.md** | Semantic (Phases 5–9) overview |
| **tests/README.md** | How to run tests |

---

## 9. Summary: Run the Entire Project

1. **Full validation (all 10 steps):**  
   `set PYTHONIOENCODING=utf-8` then `python main.py` (or `python run_all.py` or `python project_viewer.py`).

2. **Quick pipeline check:**  
   `python main.py --check "Your text"` or `threshold-onset check "Your text"`.

3. **Pipeline only:**  
   `python integration/run_complete.py "Your text"`.

4. **Health:**  
   `threshold-onset health` or `python -m threshold_onset health`.

5. **Tests:**  
   `python -m pytest tests/ threshold_onset/semantic/tests/`.

This document is the single place that describes **what the project is**, **how to execute the full project and all its codes**, and **where to find detailed documentation** based on what exists today.
