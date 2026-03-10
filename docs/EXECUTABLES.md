# All Executables — What You Can Run and What You Need to Run

---

## Enterprise CLI (Recommended)

After `pip install -e .`:

| Command | Purpose |
|---------|---------|
| `threshold-onset run` | Run full pipeline (default corpus) |
| `threshold-onset run "Your text"` | Run pipeline with custom input |
| `threshold-onset check "Your text"` | Quick user-facing check |
| `threshold-onset suite` | Full 10-step evaluation suite |
| `threshold-onset validate` | Validation only |
| `threshold-onset benchmark` | Benchmark only |
| `threshold-onset config` | Show current config (JSON) |
| `threshold-onset health` | Health check (JSON). `-v` for pipeline smoke test |

Or: `python -m threshold_onset run` (no install needed from project root).

**Health/process HTTP server:** `python scripts/health_server.py` — GET `/health`, POST `/process` (body: `{"text":"..."}`) on port 8080.

Config: `config/default.json` or `THRESHOLD_ONSET_CONFIG` env. See `docs/DEPLOYMENT.md`.

### Programmatic API

```python
from threshold_onset.api import process, ProcessResult

result = process("Your input text")
print(result.success, result.generated_outputs, result.token_count)
```

See [`docs/API.md`](API.md) for full API reference.

---

## What You NEED to Run (Essential)

| Command | Purpose |
|---------|---------|
| `python main.py` | **Full validation** — Runs all 10 steps (decoder, validation, stress, benchmark, baselines, external validation, stability, structural scaling, full pipeline). Use this to verify the system. |
| `python main.py --check "Your text"` | **Quick check** — Single pipeline run with your text. User-facing output. |
| `python integration/run_complete.py` | **Direct pipeline** — Text → structure → text. Use when you want the pipeline without the full suite. |
| `python integration/run_complete.py "Your text"` | Same with custom input. |

**Or use `project_viewer.py` (runs the same 10 steps as main.py):**
| `python project_viewer.py` | Runs all 10 steps. Same as `main.py`. |

---

## What You CAN Run (Full List)

### Root Entry Points

| Command | What it does |
|---------|--------------|
| `python main.py` | Full 10-step suite |
| `python main.py --check "text"` | Quick pipeline check |
| `python main.py --user "text"` | Full suite with your text in step 10 |
| `python main.py --user` | Interactive: prompts for text, then full suite |
| `python run_all.py` | Same as main.py |
| `main.bat` | Windows: runs main.py |
| `run_all.bat` | Windows: runs run_all.py |

### Project Viewer (Executor + Reports)

| Command | What it does |
|---------|--------------|
| `python project_viewer.py` | **Runs all 10 steps** (same as main.py) |
| `python project_viewer.py --describe` | Print overview only (no execution) |
| `python project_viewer.py --verbose` | Full module report |
| `python project_viewer.py --out FILE` | Write report to file |
| `python project_viewer.py --full --out FILE` | Full source dump of every .py |
| `python project_viewer.py --json` | Output as JSON |

### Pipeline (Integration)

| Command | What it does |
|---------|--------------|
| `python integration/run_complete.py` | Full pipeline (default corpus) |
| `python integration/run_complete.py "text"` | Full pipeline with your text |
| `python integration/run_user_result.py "text"` | User-facing output only |
| `python integration/run_user_input.py` | Quick pipeline (benchmark mode) |

### 10-Step Suite (Individual Scripts)

Run these directly if you want one step only:

| Command | Step |
|---------|------|
| `python integration/test_decoder.py` | 1. Decoder test |
| `python integration/validate_pipeline.py` | 2. Validation (7 input types) |
| `python integration/stress_test.py` | 3. Stress test (100–5000 tokens) |
| `python integration/benchmark.py` | 4. Benchmark (39 samples) |
| `python integration/baselines.py` | 5. Baselines (Random, Markov, Echo, Uniform) |
| `python integration/external_validation.py` | 6. External validation (136 samples) |
| `python integration/stability_mode.py` | 7. Stability mode |
| `python integration/stability_experiments.py` | 8. Stability experiments |
| `python integration/structural_scaling.py` | 9. Structural scaling |
| `python integration/run_complete.py` | 10. Full pipeline |

### Analysis & Tools

| Command | What it does |
|---------|--------------|
| `python integration/train.py --epochs 50 --interval 5` | Train preference learner |
| `python integration/escape_topology.py` | Escape topology measurement |
| `python integration/topology_clusters.py` | Topology clustering |
| `python integration/transition_matrix.py` | Transition permission matrix |
| `python integration/identity_permissions.py` | Identity permission profiles |
| `python integration/refusal_signatures.py` | Refusal signature analysis |
| `python integration/near_refusal_observer.py` | Near-refusal observation |
| `python integration/observe_refusals.py` | Record refusals |
| `python integration/test_invariant.py` | Invariant testing (no self-transition) |
| `python integration/test_permuted.py` | Permuted continuation test |
| `python integration/test_continuation.py` | Continuation test |
| `python integration/compare_topologies.py` | Topology comparison |
| `python integration/main_complete.py` | Alternative main (pipeline summary) |
| `python integration/main_end_to_end.py` | End-to-end run |
| `python integration/unified_system.py` | Unified system demo |

### Validation (Crush Protocol)

| Command | What it does |
|---------|--------------|
| `python validation_crush/crush_protocol.py --all` | Run all validation phases (A–I) |
| `python validation_crush/crush_protocol.py --phase A` | Run one phase (A through I) |

### Tests

| Command | What it does |
|---------|--------------|
| `python -m pytest tests/ threshold_onset/semantic/tests/` | Run all tests |
| `python tests/test_phase3_convergence.py` | Phase 3 convergence |
| `python tests/test_phase4_freeze.py` | Phase 4 freeze |
| `python threshold_onset/semantic/tests/test_integration.py` | Semantic integration |
| `python threshold_onset/semantic/tests/test_phase5.py` | Phase 5 |
| `python threshold_onset/semantic/tests/test_phase6.py` | Phase 6 |
| `python threshold_onset/semantic/tests/test_phase7.py` | Phase 7 |
| `python threshold_onset/semantic/tests/test_phase8.py` | Phase 8 |
| `python threshold_onset/semantic/tests/test_phase9.py` | Phase 9 |

### Other

| Command | What it does |
|---------|--------------|
| `python run_semantic_discovery.py` | Standalone Phases 5–9 |
| `python threshold_onset/semantic/example_complete_workflow.py` | Semantic workflow example |
| `python threshold_onset/tools/watch_version.py` | Version control watcher |
| `python test_large_context.py` | Large-context test |

---

## Save All Logs to File

```bash
python run_and_log.py              # Full run → execution_log.txt
python run_and_log.py --quick      # Quick (check + run_complete only)
python run_and_log.py --out FILE   # Custom output file
```

---

## Quick Reference: Minimum to Run

1. **Validate everything:** `python main.py` or `python project_viewer.py`
2. **Quick check with your text:** `python main.py --check "Your text"`
3. **Just the pipeline:** `python integration/run_complete.py "Your text"`
