<p align="center">
  <a href="https://github.com/chavalasantosh/THRESHOLDONSET/">
    <img
      alt="THRESHOLD_ONSET"
      src="https://github.com/chavalasantosh/THRESHOLDONSET/blob/main/Threshold(ONSET).png"
      width="100%"
    />
  </a>
</p>



# THRESHOLD_ONSET

**Phase 0: Action before Knowledge**

कार्य (kārya) happens before ज्ञान (jñāna)

---

## Aim (product goal)

**Primary aim: build the best language model (LM) this stack can produce** — strongest generation and coherence you can get from structural learning, SanTEK training, and the semantic layers, judged by **your** metrics (accuracy, tension, fluency, benchmarks, human eval).

The frozen phases and *action-before-knowledge* rule are **how** the system builds stable structure first; they are **not** the end goal. The end goal is **LM quality**.

---

[![PyPI version](https://badge.fury.io/py/threshold-onset.svg)](https://badge.fury.io/py/threshold-onset)
[![Python Versions](https://img.shields.io/pypi/pyversions/threshold-onset.svg)](https://pypi.org/project/threshold-onset)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/chavalasantosh/THRESHOLDONSET)
[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/chavalasantosh/THRESHOLDONSET)


---


## What This Is

**Scope:** This repository is a **monorepo** (many top-level folders). The Python package lives in **`threshold_onset/`** only — not the whole repo. See [`docs/architecture/FULL_ARCHITECTURE.md`](docs/architecture/FULL_ARCHITECTURE.md).

A **training and inference stack for an LM**: structural pipeline (Phases 0–4), semantic discovery (5–9), SanTEK base model (`santek_base_model.py`), and integrations. Under the hood it **explores structure emergence** through action, trace, and repetition before leaning on interpretation — that discipline is the **engineering path**, not a replacement for chasing **best LM** performance.

**Status:** **FROZEN FOREVER** — All phases (0-9), decoder, integration. See [PROJECT_FREEZE.md](PROJECT_FREEZE.md).

---

## Quick Start

### Canonical path (start here)

If the repo feels overwhelming, follow **one** path: install dev deps, run smoke tests, then choose a single runner (see `docs/architecture/GOLDEN_PATH.md`).

```bash
pip install -e ".[dev]"
python scripts/dev_check.py
```

If that passes, your checkout and import paths are sound before you touch `main.py`, training, or Docker.

### Installation

```bash
# Clone the repository
git clone https://github.com/chavalasantosh/THRESHOLDONSET.git
cd THRESHOLDONSET

# Install package (recommended for enterprise CLI)
pip install -e .

# Optional: version control tools
pip install -r requirements.txt
```

**Note:** Core system uses **Python standard library only**. Dependencies are only for optional version control tools.

### Enterprise CLI (Recommended)

```bash
# Install first: pip install -e .
threshold-onset run                    # Full pipeline
threshold-onset run "Your text"        # With custom input
threshold-onset check "Your text"      # Quick user-facing check
threshold-onset health                 # Health check (JSON)
threshold-onset config                 # Show config
```

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for Docker and env vars. [`docs/API.md`](docs/API.md) for programmatic API reference. Use `make help` for common tasks.

### Run the System (Legacy)

**Full project (recommended):**
```bash
set PYTHONIOENCODING=utf-8
python main.py
```

**Or equivalent:**
```bash
python run_all.py
```

**Quick check with your text:**
```bash
python main.py --check "Your text here"
```

**Full pipeline with your input:**
```bash
python main.py --user "Your text"
```

**Run complete pipeline directly:**
```bash
python integration/run_complete.py
```

This executes all phases:
1. **Phase 0** (THRESHOLD_ONSET) - Action → residue
2. **Phase 1** (SEGMENTATION) - Boundaries without identity
3. **Phase 2** (IDENTITY) - Identity survives across runs
4. **Phase 3** (RELATION) - Relations persist and stabilize
5. **Phase 4** (SYMBOL) - Pure aliasing layer

### Configuration

**Enterprise:** Config in `config/default.json` with env overrides (`THRESHOLD_ONSET_TOKENIZATION`, `THRESHOLD_ONSET_NUM_RUNS`, etc.). See [`docs/EXECUTION.md`](docs/EXECUTION.md).

**Legacy:** Pipeline parameters also in `integration/run_complete.py`. See [`docs/EXECUTABLES.md`](docs/EXECUTABLES.md) for all run commands.

---

## What This System Does (Simple Explanation)

**Think of it like ocean waves:**

1. **Waves appear** (Phase 0: things just happen)
2. **Waves form patterns** (Phase 1: patterns emerge)
3. **You recognize the same wave pattern** (Phase 2: identity persists)
4. **Waves influence each other** (Phase 3: relations connect)
5. **You give names to patterns** (Phase 4: pure aliasing)

**All of this happens BEFORE anyone says "this is a wave" or "this pattern is called 'swell'".**

The system works **exactly like nature works** - structure emerges before language exists.

**For a complete non-technical explanation, see:** [`docs/simple/PHASE0_TO_PHASE3_STORY.md`](docs/simple/PHASE0_TO_PHASE3_STORY.md)

---

## Phase-by-Phase Guide

### Phase 0: THRESHOLD_ONSET (FROZEN FOREVER)

**Purpose:** Prove action can exist without knowledge.

**What it does:**
- Executes structured but meaningless actions
- Produces opaque, structureless residues
- Counts repetitions and collisions

**Outputs:**
- Total residue count
- Unique residue count
- Collision rate

**Status:** ✅ **FROZEN FOREVER** - Action → residue proven

**Freeze Declaration:** [`threshold_onset/phase0/phase0/PHASE0_FREEZE.md`](threshold_onset/phase0/phase0/PHASE0_FREEZE.md)

**Key Constraints:**
- ✅ Allowed: Action, residue, repetition, persistence (counts only)
- ❌ Forbidden: Symbols, labels, meaning, interpretation, visualization

---

### Phase 1: SEGMENTATION (FROZEN FOREVER)

**Purpose:** Detect boundaries and patterns without naming them.

**What it does:**
- Detects boundaries in residue sequences (indices only)
- Clusters residues (counts only)
- Measures distances (raw numbers)
- Detects patterns (counts only)

**Outputs:**
- Boundary positions (indices)
- Cluster count and sizes
- Distance measurements
- Repetition count
- Survival count

**Status:** ✅ **FROZEN FOREVER** - Boundaries without identity

**Freeze Declaration:** [`threshold_onset/phase1/phase1/PHASE1_FREEZE.md`](threshold_onset/phase1/phase1/PHASE1_FREEZE.md)

**Key Constraints:**
- ✅ Allowed: Boundary detection, clustering, distance measurement, pattern detection
- ❌ Forbidden: Names, labels, symbols, interpretation, visualization

---

### Phase 2: IDENTITY (FROZEN FOREVER)

**Purpose:** Recognize persistent identities without naming them.

**What it does:**
- Measures persistence across multiple runs
- Detects repeatable units
- Assigns identity hashes (internal only)
- Measures stability

**Outputs:**
- Persistent segment hashes
- Identity mappings (hash-based)
- Repeatability counts
- Stability metrics

**Status:** ✅ **FROZEN FOREVER** - Identity survives across runs

**Freeze Declaration:** [`threshold_onset/phase2/phase2/PHASE2_FREEZE.md`](threshold_onset/phase2/phase2/PHASE2_FREEZE.md)

**Key Constraints:**
- ✅ Allowed: Persistence measurement, repeatable units, identity hashes (internal)
- ❌ Forbidden: Symbolic naming, linguistic labels, meaning, interpretation

**Note:** Requires multi-run mode to detect cross-run persistence.

---

### Phase 3: RELATION (FROZEN FOREVER)

**Purpose:** Detect how identities connect without naming the connections.

**What it does:**
- Constructs graph structures (hash pairs only)
- Detects interactions, dependencies, influences
- Measures relation persistence across runs
- Measures relation stability

**Outputs:**
- Graph nodes and edges (counts)
- Persistent relation hashes
- Stability ratio
- Edge density variance
- Common edges ratio

**Status:** ✅ **FROZEN FOREVER** - Relations persist and stabilize

**Freeze Declaration:** [`threshold_onset/phase3/phase3/PHASE3_FREEZE.md`](threshold_onset/phase3/phase3/PHASE3_FREEZE.md)

**Key Constraints:**
- ✅ Allowed: Graph construction, interaction detection, dependency measurement
- ❌ Forbidden: Symbolic naming, linguistic labels, graph visualization, meaning

**Validation:** Convergence tests passed (see [`tests/test_phase3_convergence.py`](tests/test_phase3_convergence.py))

---

### Phase 4: SYMBOL (FROZEN FOREVER)

**Purpose:** Create pure aliasing layer - reversible symbol mappings.

**What it does:**
- Assigns integer symbols to persistent identities
- Assigns integer symbols to persistent relations
- Creates reversible lookup tables (both directions)
- Adds zero new structure

**Outputs:**
- Identity alias count
- Relation alias count

**Status:** ✅ **FROZEN FOREVER** - Pure aliasing, reversible

**Freeze Declaration:** [`threshold_onset/phase4/phase4/PHASE4_FREEZE.md`](threshold_onset/phase4/phase4/PHASE4_FREEZE.md)

**Key Constraints:**
- ✅ Allowed: Integer symbols only (0, 1, 2, 3...), reversible mappings
- ❌ Forbidden: Meaning, interpretation, structural modification, symbol sequences

**Critical Rule:** Removing Phase 4 restores Phase 3 exactly (bit-for-bit, no recomputation).

**Validation:** Freeze validation tests passed (see [`tests/test_phase4_freeze.py`](tests/test_phase4_freeze.py))

---

## Understanding Outputs

### Phase 0 Output Example

```
THRESHOLD_ONSET — Phase 0 (Finite Variant)

Total residue count:     200
Unique residue count:     10
Collision rate:           0.9500
```

**What this means:**
- 200 actions produced 200 residues
- Only 10 unique values (high reuse)
- 95% collision rate (same values repeat)

### Phase 1 Output Example

```
THRESHOLD_ONSET — Phase 1

Boundary positions:       [1, 2, 3, ...]
Cluster count:             10
Repetition count:          362
Survival count:            0
```

**What this means:**
- Boundaries detected at specific positions (indices)
- 10 clusters found
- 362 repetitions detected
- No survival across runs (single-run mode)

### Phase 2 Output Example (Multi-Run)

```
THRESHOLD_ONSET — Phase 2 (Multi-Run)

Persistent segments:       99
Identity mappings:          99
Repeatable units:           99
```

**What this means:**
- 99 segments persist across multiple runs
- 99 identities assigned (hash-based, internal)
- 99 repeatable units detected

### Phase 3 Output Example

```
THRESHOLD_ONSET — Phase 3 (Multi-Run)

Node count:                 201
Edge count:                  4950
Persistent relations:        5960
Stability ratio:             1.0000
```

**What this means:**
- 201 nodes in relation graph
- 4950 edges (connections)
- 5960 relations persist across runs
- Perfect stability (1.0 = no variance)

### Phase 4 Output Example

```
THRESHOLD_ONSET — Phase 4 (Multi-Run)

Identity alias count:       99
Relation alias count:        5960
```

**What this means:**
- 99 identities have integer aliases
- 5960 relations have integer aliases
- Pure aliasing (no structure added)

---

## Project Viewer

To see a comprehensive view of the entire project (all modules, docstrings, structure):

```bash
python project_viewer.py              # Print to console
python project_viewer.py --out VIEW.txt   # Write report
python project_viewer.py --full --out FULL.txt   # Full source of every file
```

Excludes `main.py` from the view. See all 149+ Python files, pipeline flow, and module roles.

---

## Project Structure

```
THRESHOLD_ONSET/
├── main.py                          # Primary entry point (10-step suite)
├── run_all.py                       # Equivalent to main.py
├── project_viewer.py                # Comprehensive project explorer
├── README.md                        # This file
├── requirements.txt                 # Dependencies (optional)
│
├── threshold_onset/                 # Core package
│   ├── phase0/                      # Phase 0 (FROZEN)
│   │   ├── phase0.py                 # Core pipeline
│   │   ├── actions.py                # Action variants
│   │   └── phase0/                   # Phase 0 documentation
│   ├── phase1/                      # Phase 1 (FROZEN)
│   │   ├── phase1.py                # Segmentation pipeline
│   │   ├── boundary.py              # Boundary detection
│   │   ├── cluster.py               # Clustering
│   │   ├── distance.py              # Distance measurement
│   │   └── pattern.py               # Pattern detection
│   ├── phase2/                      # Phase 2 (FROZEN)
│   │   ├── phase2.py                # Identity pipeline
│   │   ├── persistence.py           # Persistence measurement
│   │   ├── repeatable.py            # Repeatable units
│   │   ├── identity.py              # Identity hashes
│   │   └── stability.py             # Stability metrics
│   ├── phase3/                      # Phase 3 (FROZEN)
│   │   ├── phase3.py                # Relation pipeline
│   │   ├── relation.py              # Relation extraction
│   │   ├── persistence.py           # Relation persistence
│   │   ├── stability.py             # Relation stability
│   │   ├── graph.py                 # Graph construction
│   │   ├── interaction.py           # Interaction detection
│   │   ├── dependency.py            # Dependency measurement
│   │   └── influence.py             # Influence metrics
│   ├── phase4/                      # Phase 4 (FROZEN)
│   │   ├── phase4.py                # Symbol pipeline
│   │   ├── alias.py                 # Alias assignment
│   │   └── phase4/                  # Phase 4 documentation
│   ├── identity_conditioned/        # (source, content) → outcome accumulator
│   ├── phase10/                     # Phase 10 — directed continuation (post 0–4)
│   ├── semantic/                    # Phases 5-9 (semantic discovery)
│   └── tools/                       # Version control tools
│       ├── version_control.py
│       └── watch_version.py
│
├── integration/                     # Unified system (threshold_onset + santok)
│
├── docs/                            # Project documentation
│   ├── axioms/                      # Core design constraints
│   ├── architecture/                # System architecture
│   ├── simple/                      # Non-technical explanations
│   ├── history/                     # Project history
│   └── README.md                    # Documentation overview
│
├── tests/                            # Test suite
│   ├── test_phase3_convergence.py   # Phase 3 validation test
│   └── test_phase4_freeze.py        # Phase 4 validation test
│
└── versions/                        # Version snapshots (auto)
```

---

## Documentation

### Core Documentation

- **Phase map (single source of truth):** [`docs/CANONICAL_PHASE_MAP.md`](docs/CANONICAL_PHASE_MAP.md) — structural 0–4 + **phase10** vs **semantic 5–9** (only one Phase 5).
- **Consolidated changelog-style summary:** [`docs/RECENT_DEVELOPMENTS.md`](docs/RECENT_DEVELOPMENTS.md) — Phase 10, API, identity-conditioned layer, removed duplicate Phase 5, tests, fixes.
- **Execution:** [`docs/EXECUTION.md`](docs/EXECUTION.md) - How to run (commands, modes, config)

### Pipeline environment (`integration/run_complete.py`)

| Variable | Effect |
|----------|--------|
| `PIPELINE_PHASE10_METRICS` | `1` / `true` — when `return_model_state=True`, add `phase10_metrics` to `model_state` |
| `PIPELINE_PHASE10_CROSS_CHECK_PHASE3` | With the above, count only transitions allowed by Phase 3 undirected edges |

Related: `SEMANTIC_LOG_PHASE10=1` for `run_semantic_discovery.py`; `SANTEK_PHASE10_MERGED_DEBUG=1` for merged multi-tokenizer Phase 10 DEBUG lines during SanTEK init (see `integration/model/santek_base.py`); `SANTEK_PHASE10_TRAINING_SUMMARY=1` writes `meta.phase10_training_summary` on the final SanTEK base model JSON.

Design note (source × content continuation, not “halo” as bias): [`docs/IDENTITY_CONDITIONED_CONTINUATION.md`](docs/IDENTITY_CONDITIONED_CONTINUATION.md).
- **Axioms:** [`docs/axioms/AXIOMS.md`](docs/axioms/AXIOMS.md) - Non-negotiable design constraints
- **Architecture:** [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) - System architecture
- **Phase Status:** [`docs/PHASE_STATUS_CANONICAL.md`](docs/PHASE_STATUS_CANONICAL.md) - Authoritative phase status

### Simple Explanations (Non-Technical)

- **Complete Story:** [`docs/simple/PHASE0_TO_PHASE3_STORY.md`](docs/simple/PHASE0_TO_PHASE3_STORY.md) - What we built (for everyone)
- **Independence Check:** [`docs/simple/INDEPENDENCE_CHECK.md`](docs/simple/INDEPENDENCE_CHECK.md) - Why Phase 4 is safe

### Phase Documentation

Each phase has its own documentation:
- **Phase 0:** `threshold_onset/phase0/phase0/docs/`
- **Phase 1:** `threshold_onset/phase1/phase1/`
- **Phase 2:** `threshold_onset/phase2/phase2/`
- **Phase 3:** `threshold_onset/phase3/phase3/`
- **Phase 4:** `threshold_onset/phase4/phase4/`
- **Phase 10 (structural continuation metrics):** `threshold_onset/phase10/README.md`

### Freeze Declarations

All phases are frozen with official declarations:
- **Phase 0:** [`threshold_onset/phase0/phase0/PHASE0_FREEZE.md`](threshold_onset/phase0/phase0/PHASE0_FREEZE.md)
- **Phase 1:** [`threshold_onset/phase1/phase1/PHASE1_FREEZE.md`](threshold_onset/phase1/phase1/PHASE1_FREEZE.md)
- **Phase 2:** [`threshold_onset/phase2/phase2/PHASE2_FREEZE.md`](threshold_onset/phase2/phase2/PHASE2_FREEZE.md)
- **Phase 3:** [`threshold_onset/phase3/phase3/PHASE3_FREEZE.md`](threshold_onset/phase3/phase3/PHASE3_FREEZE.md)
- **Phase 4:** [`threshold_onset/phase4/phase4/PHASE4_FREEZE.md`](threshold_onset/phase4/phase4/PHASE4_FREEZE.md)

---

## Testing & Validation

### Phase 3 Convergence Test

Validates Phase 3 stability across multiple run counts:

```bash
python tests/test_phase3_convergence.py
```

**What it tests:**
- Gate passes consistently
- Stability ratio stays ≥ threshold
- Metrics converge (no drift)
- No flaky behavior

### Phase 4 Freeze Validation

Validates Phase 4 freeze-worthiness:

```bash
python tests/test_phase4_freeze.py
```

**What it tests:**
- Determinism (same inputs → same outputs)
- Reversibility (removing Phase 4 restores Phase 3)
- Immutability (aliases never change)
- Gate determinism (gate never flakes)

### Optional: SanTEK + Phase 10 training meta (slow)

Heavy integration test (full pipeline init + 1 epoch). Opt-in:

```bash
RUN_SANTEK_PHASE10_META_TEST=1 python -m pytest tests/test_santek_phase10_meta_optional.py -m slow -v
```

Asserts `meta.phase10_training_summary` on the written base model JSON when `SANTEK_PHASE10_TRAINING_SUMMARY=1` (the test sets this via env).

---

## Version Control

The project includes a local version control system (optional):

```bash
python threshold_onset/tools/watch_version.py
```

**Features:**
- File watching with `watchfiles`
- Content hashing with SHA256
- SQLite metadata storage
- Unified diffs between versions

See [`threshold_onset/tools/docs/VERSION_CONTROL.md`](threshold_onset/tools/docs/VERSION_CONTROL.md) for details.

---

## Code Standards

- **Python standard library only** (except optional version control tools)
- **Clean, minimal code**
- **Phase boundaries strictly enforced**
- **Each phase operates independently**
- **Documentation co-located with code**

---

## Philosophy

**Core Axiom:**

> कार्य (kārya) happens before ज्ञान (jñāna)
>
> Function stabilizes before knowledge appears.

**What this means:**

- Action exists before meaning
- Structure emerges before language
- Patterns form before names
- Identity persists before symbols
- Relations connect before interpretation

**The system proves:**

- Things can exist and work together **BEFORE** anyone gives them names
- Structure emerges naturally through action and repetition
- Identity and relations are discovered, not created
- Symbols are pure aliases - reversible, meaningless labels

---

## Current Status

**All Phases: FROZEN FOREVER**

| Phase | Name | Status | Freeze Declaration |
|-------|------|--------|-------------------|
| Phase 0 | THRESHOLD_ONSET | ✅ FROZEN | [`threshold_onset/phase0/phase0/PHASE0_FREEZE.md`](threshold_onset/phase0/phase0/PHASE0_FREEZE.md) |
| Phase 1 | SEGMENTATION | ✅ FROZEN | [`threshold_onset/phase1/phase1/PHASE1_FREEZE.md`](threshold_onset/phase1/phase1/PHASE1_FREEZE.md) |
| Phase 2 | IDENTITY | ✅ FROZEN | [`threshold_onset/phase2/phase2/PHASE2_FREEZE.md`](threshold_onset/phase2/phase2/PHASE2_FREEZE.md) |
| Phase 3 | RELATION | ✅ FROZEN | [`threshold_onset/phase3/phase3/PHASE3_FREEZE.md`](threshold_onset/phase3/phase3/PHASE3_FREEZE.md) |
| Phase 4 | SYMBOL | ✅ FROZEN | [`threshold_onset/phase4/phase4/PHASE4_FREEZE.md`](threshold_onset/phase4/phase4/PHASE4_FREEZE.md) |

**Phase 10 (structural, not frozen with 0–4):** directed continuation analytics on **ordered identity streams** — empirical successor counts, exclusion (never-seen successors within the observed universe), and strict-dominance **necessity**. Optional cross-check against Phase 3 undirected edges. Does **not** modify Phase 0–4 pipelines. See [`threshold_onset/phase10/README.md`](threshold_onset/phase10/README.md).

**System:** ✅ **FOUNDATION COMPLETE**

All phases have been validated, frozen, and documented. The foundational construction is complete.

---

## Semantic Discovery Module (Phases 5-9)

**Status**: ✅ **COMPLETE** - Enterprise-grade semantic understanding system

A module built on the frozen foundation (Phases 0–4) that implements automatic semantic understanding and fluent output generation from first principles. **Phase 10** (under `threshold_onset/phase10/`) is a separate **structural** metrics layer (directed continuation); it is **not** part of this semantic stack.

**Location**: `threshold_onset/semantic/`

**What it does:**
- **Phase 5**: Measures how structures affect future possibilities (consequence field)
- **Phase 6**: Discovers meaning clusters from consequence vectors
- **Phase 7**: Emerges functional roles from cluster properties
- **Phase 8**: Discovers grammar-like constraints from role patterns
- **Phase 9**: Generates fluent sequences using stability + novelty + templates

**Key Features:**
- ✅ All from first principles (no neural networks, no imported linguistics)
- ✅ Multiple probe policies for policy-invariant measurement
- ✅ Empirical entropy from actual behavior
- ✅ Counterfactual edge deltas
- ✅ Stability-based clustering
- ✅ Quantile-based role assignment
- ✅ Global forbidden pattern comparison
- ✅ Prefix-match template scoring
- ✅ Experience table (derived from consequences)

**Documentation**: See [`threshold_onset/semantic/README.md`](threshold_onset/semantic/README.md) for complete documentation.

**Quick Start**:
```python
from threshold_onset.semantic import (
    ConsequenceFieldEngine,
    MeaningDiscoveryEngine,
    RoleEmergenceEngine,
    ConstraintDiscoveryEngine,
    FluencyGenerator
)

# Build complete semantic discovery pipeline
# (See threshold_onset/semantic/COMPLETE_SYSTEM_GUIDE.md)
```

---

## SanTEK base model (`santek_base_model.py` / `integration/model/santek_base.py`)

Training writes **one JSON file** (default `output/santek_base_model.json`). The trainer updates that same path:

- **Immediately after INIT** (post-init merged graph + `meta.checkpoint.phase=post_init`, skipped corpus indices, timing).
- **After every epoch** (`phase=epoch_end`, epoch number, mean tension, accuracy).
- **Final atomic replace** when training finishes (`phase=training_complete` + full `path_scores` / `vocab`).

`meta.epoch_trace` holds a compact per-epoch history for dashboards and sanity checks (e.g. epoch 1 vs later accuracy, tension trend).

### Environment variables

| Variable | Effect |
|----------|--------|
| `SANTEK_TRAIN_FAST=1` | Default is already fast (`1`); when fast path is active and you have not set the skip vars below, SanTEK may inject them for lighter pipeline work. Set to `0` to prefer full pipeline work (subject to other env). |
| `PHASE1_SKIP_DISTANCES=1` | Skip Phase 1 distance work inside the pipeline (large speedup; used with fast training). |
| `PHASE3_SKIP_PATH_LENGTHS=1` | Skip Phase 3 path-length work inside the pipeline (speedup; used with fast training). |
| `SANTEK_PIPELINE_VERBOSE=1` | More pipeline logging during SanTEK training. |
| `SANTEK_INCLUDE_BYTE=1` | Include the **byte** tokenizer in the default method list (normally skipped; use for byte-specific runs / `*_v1_byte.json`). |
| `SANTEK_DISABLE_CHECKPOINT=1` | No mid-run writes; **only** the final atomic save (faster disk, less resilience). |
| `SANTEK_CHECKPOINT_SYNC=1` | Run checkpoint serialization on the main thread (debug / avoid background writer). |
| `SANTEK_CHECKPOINT_PRETTY=1` | Indented JSON for async checkpoint writes (larger files). |
| `SANTEK_TEXT_WORKERS` / `SANTEK_METHOD_WORKERS` | **Parallelism only** (concurrent texts / concurrent method-tasks). They do **not** add tokenizers or enable `byte`. Use `1`/`1` for quieter logs or to debug closed-file races. |
| `PIPELINE_PHASE10_METRICS=1` | Each tokenizer’s pipeline run may attach `phase10_metrics` on that run’s `model_state` (via `PipelineConfig`). |
| `SANTEK_PHASE10_MERGED_DEBUG=1` | DEBUG log merged multi-tokenizer Phase 10 per corpus text (serial loop + process workers). |
| `SANTEK_PHASE10_TRAINING_SUMMARY=1` | Accumulate compact Phase 10 stats per text; final JSON gets `meta.phase10_training_summary`. |

### Troubleshooting

- **`I/O operation on closed file`**: Often concurrent pipeline workers + stdio redirection; try worker count `1` as above, or ensure you are on a build with the pipeline stdio lock (see `santek_base.py`).
- **Skipped corpus rows**: Check printed **Skipped corpus indices** after init; common causes are empty/binary/non-text or tokenizers returning no tokens for that script.
- **Metrics**: `best_tension` is the **lowest** mean epoch tension seen (lower = structurally “easier” in that metric). Per-epoch tension can still rise while best tracks the minimum.

---

## What's Next?

**The foundational system (Phases 0-4) is complete and frozen.** 

**The Semantic Discovery Module (Phases 5-9) extends this foundation** to demonstrate how meaning, roles, constraints, and fluency can emerge automatically from structure, without importing external knowledge.

**Possible future directions:**
- Grounding to external sensors/actions
- Multi-modal understanding
- Application-specific extensions
- Performance optimization

---

## License

This project is a foundational research system exploring structure emergence before language.

---

## Contact & Repository

- **Repository:** https://github.com/chavalasantosh/THRESHOLDONSET.git
- **Author:** ChavalaSantosh

---

## Acknowledgments

This system is built on the principle that **function stabilizes before knowledge appears**.

**The system proves:**
- Action can exist without knowledge
- Structure can emerge without language
- Identity can persist without names
- Relations can connect without interpretation
- Symbols can alias without meaning

**All of this happens before anyone says "this is X" or "this means Y".**

---

**For detailed information, see the documentation in `docs/` and phase-specific documentation in `threshold_onset/phaseX/`.**
