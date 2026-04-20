# Architecture (`docs/architecture/`)

System architecture and design documentation for the THRESHOLD_ONSET repository.

## Contents

### [`FULL_ARCHITECTURE.md`](FULL_ARCHITECTURE.md)

**Start here for scope:** explains the difference between the **whole repository** (monorepo root) and the **`threshold_onset/` package** folder — they are not the same thing.

### [`WORKFLOW_AND_PROCESS.md`](WORKFLOW_AND_PROCESS.md)

**Workflow diagrams** (Mermaid): how processing flows (phases, SanTEK train/generate), API path, and **clean development process** — framed like an architecture diagram, honest about “not a standard transformer backprop stack.”

### [`GOLDEN_PATH.md`](GOLDEN_PATH.md)

**Operational path:** one install + test path, a small command table (runners, data/Git rules).

### [`ARCHITECTURE.md`](ARCHITECTURE.md)

Full **current-directory** codebase map:

- High-level layer diagram (entry → integration → core → optional)
- Physical repository layout table
- `threshold_onset` package (phases 0–4, semantic 5–9, corpus_state, CLI/API)
- `integration/run_complete.py` orchestrator and sequence diagram
- SanTEK base model stack and training data-flow diagram
- `build_hindu_corpus.py` and other entry points
- Configuration, environment variables, dependencies philosophy
- Summary mental model

## Purpose

This documentation explains:

1. How the repository is organized today (not legacy `phase0/` at repo root)
2. How the unified pipeline and SanTEK training relate
3. Where corpus state and model artifacts live (`output/`)
4. How optional subsystems (`santok_complete`, `validation_crush`) attach

## Architecture principles

1. **Phase model** — strict structural boundaries (0–4) before semantic layers (5–9)
2. **Co-location** — documentation with code where possible
3. **Minimal dependencies** — stdlib on core path; optional `rich`, SanTOK
4. **Frozen phases** — see root `PROJECT_FREEZE.md` / README

## Related documentation

- Root [README.md](../../README.md) — quick start, `threshold-onset` CLI
- [EXECUTION.md](../EXECUTION.md) — env vars and execution
- [Semantic package architecture](../../threshold_onset/semantic/ARCHITECTURE.md) — phases 5–9 internals
- [AXIOMS](../axioms/AXIOMS.md) — design constraints
