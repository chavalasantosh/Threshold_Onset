# What You Ran — and What Else Exists

This doc explains **what the terminal output from `python main.py` is**, and **what other parts of the project exist** that are not run by `main.py`.

---

## What You Just Ran: The 10-Step Evaluation Suite

When you run:

```bash
set PYTHONIOENCODING=utf-8
python main.py
```

you run the **Full Evaluation Suite**. It is a **validation harness**: it runs 10 separate scripts one after another and reports PASS/FAIL. It does **not** run every script in the project.

### What each step does (in plain language)

| Step | Name | What it does |
|------|------|----------------|
| 1 | **Decoder test** | Builds a symbol decoder from a tiny corpus and checks that decoding works (symbols → words). |
| 2 | **Validation** | Runs the pipeline on 7 fixed input types (short, normal, repeated, single token, long, punctuation, mixed) and checks all pass. |
| 3 | **Stress test** | Runs the pipeline on 100, 500, 1000, 2000, 5000 tokens to check it doesn’t break at scale. |
| 4 | **Benchmark** | Runs 39 predefined samples and reports success rate, decoder consistency, and constraint violations (should be 0). |
| 5 | **Baselines** | Compares THRESHOLD_ONSET to 4 baselines (random, markov1, echo, uniform); shows that the pipeline achieves 0% self-transition vs baselines. |
| 6 | **External validation** | Runs 136 external samples; reports success rate and 0 violations. |
| 7 | **Stability mode** | Runs the pipeline with dropout perturbation to see which identities persist across runs. |
| 8 | **Stability experiments** | Parameter sweep (drop_prob, K, theta) and recurrence tables; shows phase boundary p* = 1 - sqrt(theta/K). |
| 9 | **Structural scaling** | Varies input size (3 to 100 tokens) and reports identities, relations, escape topology, diversity. |
| 10 | **Full pipeline** | Runs the **actual** end-to-end pipeline (tokenize → phases 0–4 → continuation → topology → clustering → scoring → surface → generation) and prints the end-user result. |

So: **steps 1–9 are tests/experiments**; **step 10 is the real pipeline** you’d use in practice.

---

## This Is Not Everything: What Else You Can Run

`main.py` runs **only** those 10 scripts. The project has many more runnables that are **not** part of this suite.

### Other ways to run the pipeline

| Command | What it does |
|--------|----------------|
| `python integration/run_complete.py "Your text"` | Same pipeline as step 10, with your text (no suite). |
| `python main.py --check "Your text"` | Quick run: only the pipeline with your text, user-facing output. |
| `threshold-onset run "Your text"` | Same via CLI (after `pip install -e .`). |
| `python integration/main_complete.py` | Alternative “complete” pipeline with a different layout. |
| `python integration/main_end_to_end.py` | Another end-to-end script (standalone). |
| `python integration/run_complete.py --no-tui "Your text"` | Same pipeline, minimal TUI. |
| `python integration/model_predict_next.py "Your text"` | Next-identity accuracy (model). |
| `python integration/model_predict_next.py --learn "Your text"` | Same with online learning. |

**PowerShell (Windows):** Use `;` to chain commands (not `&&`). Use `$env:PYTHONIOENCODING="utf-8"` (not `set`). Example: `cd "path\to\repo"; $env:PYTHONIOENCODING="utf-8"; python integration/model_predict_next.py "Your text"`

### Training and analysis (not in main.py)

| Command | What it does |
|--------|----------------|
| `python integration/train.py --epochs 50 --interval 5` | Trains the preference learner over many epochs. |
| `python integration/run_corpus_scale.py` | Corpus-scale run (multiprocessing). |
| `python integration/run_corpus_stress.py` | Corpus stress run. |
| `python integration/refusal_signatures.py` | Refusal signature aggregation. |
| `python integration/observe_refusals.py` | Record refusals. |
| `python integration/escape_topology.py` | Escape topology measurement. |
| `python integration/topology_clusters.py` | Topology clustering. |
| `python integration/scoring.py` | Path scoring (main). |
| `python integration/compare_topologies.py` | Topology comparison. |

### Semantic discovery (Phases 5–9, not in main.py)

| Command | What it does |
|--------|----------------|
| `python run_semantic_discovery.py` | Standalone Phases 5–9 semantic discovery. |
| `python threshold_onset/semantic/example_complete_workflow.py` | Example semantic workflow. |

### Validation and tests (not the 10-step suite)

| Command | What it does |
|--------|----------------|
| `python validation_crush/crush_protocol.py --all` | Crush validation (phases A–I). |
| `python validation_crush/crush_protocol.py --phase A` | Single crush phase. |
| `python -m pytest tests/ threshold_onset/semantic/tests/` | All unit/integration tests. |

### Servers and tools

| Command | What it does |
|--------|----------------|
| `python scripts/health_server.py` | HTTP server: GET /health, POST /process (port 8080). |
| `python project_viewer.py --describe` | Project overview (no execution). |
| `python project_viewer.py --verbose` | Verbose module report. |
| `python run_and_log.py` | Same 10 steps as main.py, output appended to `execution_log.txt`. |
| `python run_and_log.py --quick` | Only quick check + run_complete, logged. |

### One-off / examples

| Command | What it does |
|--------|----------------|
| `python integration/test_invariant.py` | Invariant test (no self-transition). |
| `python integration/test_permuted.py` | Permuted continuation test. |
| `python integration/test_continuation.py` | Continuation test. |
| `python integration/near_refusal_observer.py` | Near-refusal observation. |
| `python integration/unified_system.py` | Unified system demo. |
| `python integration/generate.py` | Generation test. |
| `python test_large_context.py` | Large-context test. |

---

## Summary

- **What you ran:** The **10-step evaluation suite** (`main.py`). It runs 10 scripts in order: 9 validation/experiment steps + 1 full pipeline run. The last step is the “real” pipeline.
- **What you didn’t run:** Training, corpus-scale/stress runs, refusal analysis, semantic discovery, crush validation, pytest, health server, project viewer reports, and all other scripts listed above.
- **To run “everything” in one go:** There is no single command that runs every script in the repo. The closest is `python main.py` (the 10-step suite). For a full picture of all runnables, see **docs/EXECUTABLES.md** and **docs/FULL_PROJECT_DOCUMENTATION.md**.
