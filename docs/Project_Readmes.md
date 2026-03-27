# THRESHOLD_ONSET — Complete Project Guide

**Phase 0: Action before Knowledge**

कार्य (kārya) happens before ज्ञान (jñāna)

---

## What This Is

THRESHOLD_ONSET is a foundational system that explores how structure emerges through action, trace, and repetition — **before** symbols, meaning, or interpretation exist.

**Core Principle:** Function stabilizes before knowledge appears.

**What It Proves:** Things can exist, form patterns, recognize each other, and connect — all **without names, labels, or meaning**.

---

## Current Status

**All Phases Complete and Frozen:**

- **Phase 0** (THRESHOLD_ONSET): ✅ **FROZEN FOREVER** — Action → residue proven
- **Phase 1** (SEGMENTATION): ✅ **FROZEN FOREVER** — Boundaries without identity
- **Phase 2** (IDENTITY): ✅ **FROZEN FOREVER** — Identity survives across runs
- **Phase 3** (RELATION): ✅ **FROZEN FOREVER** — Relations persist and stabilize
- **Phase 4** (SYMBOL): ✅ **FROZEN FOREVER** — Pure aliasing layer

**System:** ✅ **FOUNDATION COMPLETE** — All phases frozen, system ready for use

See `docs/PHASE_STATUS_CANONICAL.md` for authoritative status.

---

## Quick Start

### Installation

1. **Requirements:**
   - Python 3.8 or higher
   - Standard library only (core system)
   - Optional: `watchfiles` for version control

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation:**
   ```bash
   python main.py
   ```

### Basic Execution

```bash
python main.py
```

This will:
1. Execute Phase 0 (action variants) — generates residues
2. Run Phase 1 (segmentation) — detects boundaries and clusters
3. Run Phase 2 (identity detection) — finds persistent identities
4. Run Phase 3 (relation detection) — maps connections between identities
5. Run Phase 4 (symbol assignment) — creates aliases for identities and relations

**Configuration:** Edit `integration/run_complete.py` to select:
- Tokenization method (`tokenization_method`)
- Number of runs (`num_runs`) for multi-run persistence

---

## What This System Does (Simple Explanation)

**Think of it like discovering a new planet:**

1. **Phase 0:** We landed and saw **things happening** (like seeing geysers erupt)
   → We proved: "Things can happen here"

2. **Phase 1:** We noticed **patterns** (like seeing geysers erupt in groups)
   → We proved: "Patterns exist here"

3. **Phase 2:** We recognized **things that come back** (like the same geyser erupting daily)
   → We proved: "Some things persist here"

4. **Phase 3:** We saw **how things connect** (like geysers affecting nearby plants)
   → We proved: "Things are connected here"

5. **Phase 4:** We created **name tags** for things that already exist
   → We proved: "We can reference what exists without changing it"

**But we STILL haven't named anything with meaning.**

We haven't said:
- "This geyser is called 'Old Faithful'"
- "This pattern is called 'eruption cycle'"
- "This connection is called 'ecosystem'"

**We just discovered, measured, mapped, and indexed.**

**For a complete non-technical explanation, see:** `docs/simple/PHASE0_TO_PHASE3_STORY.md`

---

## Phase-by-Phase Guide

### Phase 0: THRESHOLD_ONSET (FROZEN FOREVER)

**Purpose:** Prove that action can exist without knowledge.

**What It Does:**
- Executes structured but meaningless actions
- Produces opaque, structureless residues (float values 0.0-1.0)
- Counts residues, unique residues, and collisions

**What It Outputs:**
- Total residue count
- Unique residue count
- Collision rate

**Status:** ✅ **FROZEN FOREVER**

**Freeze Declaration:** `threshold_onset/phase0/phase0/PHASE0_FREEZE.md`

**Key Constraints:**
- ✅ Allowed: Action, residue, repetition, persistence, survival (counts only)
- ❌ Forbidden: Symbols, labels, names, meaning, interpretation, visualization, statistics beyond counts

**Action Variants:**
- `noise_baseline`: Pure random (frozen baseline)
- `inertia`: Temporal correlation
- `random_walk`: Bounded random walk
- `oscillator`: Bounded oscillator
- `decay_noise`: Decay toward target + noise
- `finite`: Discrete but meaningless (enables exact equality)

---

### Phase 1: SEGMENTATION (FROZEN FOREVER)

**Purpose:** Detect boundaries and patterns without naming them.

**What It Does:**
- Detects boundaries in residue sequences (indices only)
- Clusters residues by similarity (counts only)
- Measures distances between residues (raw numbers)
- Detects repetition patterns (counts only)

**What It Outputs:**
- Boundary positions (indices)
- Cluster count and sizes (numbers)
- Distance count
- Repetition count
- Survival count

**Status:** ✅ **FROZEN FOREVER**

**Freeze Declaration:** `threshold_onset/phase1/phase1/PHASE1_FREEZE.md`

**Key Constraints:**
- ✅ Allowed: Boundary detection (indices), difference measurement (raw numbers), clustering (counts), pattern detection (counts)
- ❌ Forbidden: Names, labels, symbols, interpretation, visualization, adaptive thresholds, real-time logs

---

### Phase 2: IDENTITY (FROZEN FOREVER)

**Purpose:** Recognize persistent identities without naming them.

**What It Does:**
- Measures persistence across multiple runs (counts only)
- Detects repeatable units (counts only)
- Assigns identity hashes (internal only, hash-based)
- Measures stability metrics (counts only)

**What It Outputs:**
- Persistence count
- Persistent segments (hash list, internal)
- Repeatability count
- Repeatable units (hash list, internal)
- Identity mappings (hash → hash, internal)
- Identity persistence count
- Stability count
- Stable clusters (hash list, internal)

**Status:** ✅ **FROZEN FOREVER**

**Freeze Declaration:** `threshold_onset/phase2/phase2/PHASE2_FREEZE.md`

**Key Constraints:**
- ✅ Allowed: Persistence measurement (counts), repeatable unit detection (counts), identity hash generation (internal only), stability metrics (counts)
- ❌ Forbidden: Symbolic naming, linguistic labels, meaning, interpretation, using identity hashes as names, visualization, adaptive thresholds

**Note:** Requires multi-run mode to detect cross-run persistence.

---

### Phase 3: RELATION (FROZEN FOREVER)

**Purpose:** Map connections between identities without naming them.

**What It Does:**
- Constructs graph structures (hash pairs only)
- Detects interactions (counts and hash pairs)
- Measures dependencies (counts and hash pairs)
- Computes influence metrics (numbers only)
- Measures relation persistence across runs
- Measures relation stability (normalized frequencies)

**What It Outputs:**
- Node count
- Edge count
- Total relations
- Persistent relations
- Persistence rate
- Stable relations
- Stability ratio
- Common edges ratio
- Edge density variance
- Path lengths

**Status:** ✅ **FROZEN FOREVER**

**Freeze Declaration:** `threshold_onset/phase3/phase3/PHASE3_FREEZE.md`

**Key Constraints:**
- ✅ Allowed: Graph structure construction (hash pairs), interaction detection (counts and hash pairs), dependency measurement (counts and hash pairs), influence metrics (numbers)
- ❌ Forbidden: Symbolic naming, linguistic labels, meaning, interpretation, graph visualization, node/edge labels, adaptive thresholds

**Validation:** Convergence tests passed (NUM_RUNS = 5, 10, 20), stability ratio = 1.0000, gate passes 100% of the time.

---

### Phase 4: SYMBOL (FROZEN FOREVER)

**Purpose:** Create reversible aliases for identities and relations.

**What It Does:**
- Assigns integer symbols to persistent identities (0, 1, 2, 3...)
- Assigns integer symbols to persistent relations (0, 1, 2, 3...)
- Creates reversible mappings (hash ↔ symbol, both directions)
- Maintains append-only immutability

**What It Outputs:**
- Identity alias count
- Relation alias count

**Status:** ✅ **FROZEN FOREVER**

**Freeze Declaration:** `threshold_onset/phase4/phase4/PHASE4_FREEZE.md`

**Key Constraints:**
- ✅ Allowed: Pure aliasing, integer symbols only, deterministic assignment, reversible mappings
- ❌ Forbidden: Adding structure, storing symbol sequences, semantic content, meaning, interpretation

**Critical Property:** Removing Phase 4 restores Phase 3 exactly (bit-for-bit, without recomputation).

**Validation:** Freeze validation tests passed (determinism, reversibility, immutability, gate determinism).

---

## Installation & Setup

### Requirements

- **Python:** 3.8 or higher
- **Dependencies:** See `requirements.txt`
  - `watchfiles>=0.21.0` (for version control tools only)
  - `pylint>=3.0.0` (for code quality)
  - `numpy` (for numerical operations)

**Note:** Core system uses Python standard library only. Dependencies are for tools and development.

### Installation Steps

1. **Clone or download the project:**
   ```bash
   cd THRESHOLD_ONSET
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python main.py
   ```

4. **Expected output:**
   - Phase 0 execution (residue counts)
   - Phase 1 execution (boundaries, clusters)
   - Phase 2 execution (persistent identities)
   - Phase 3 execution (persistent relations)
   - Phase 4 execution (alias counts)

---

## Running the System

### Basic Execution

```bash
python main.py
```

### Configuration Options

Edit `integration/run_complete.py` to configure execution (around line 557):

```python
tokenization_method = "word"   # or "character", "grammar", etc.
num_runs = 3                   # Phase 0 runs for multi-run persistence
```

### Execution Modes

**Single-Run Mode** (`num_runs = 1`):
- Runs Phase 0 once
- Tests repeatability within one run
- Cannot detect cross-run persistence
- Use for: Testing action variants, debugging, quick validation

**Multi-Run Mode** (`num_runs > 1`):
- Runs Phase 0 N times (independent runs)
- Tests persistence across multiple runs
- Enables persistent segment detection
- Use for: Full system validation, persistence testing, identity survival

See `docs/EXECUTION_MODES.md` for detailed information.

---

## Understanding Outputs

### Phase 0 Outputs

```
THRESHOLD_ONSET — Phase 0 (Finite Variant)

Total residue count:     200
Unique residue count:     10
Collision rate:           0.9500
```

**What This Means:**
- **Total residue count:** Number of actions executed
- **Unique residue count:** Number of distinct residue values
- **Collision rate:** Fraction of residues that are duplicates (repetition indicator)

### Phase 1 Outputs

```
THRESHOLD_ONSET — Phase 1

Boundary positions:        [1, 2, 3, ...]
Cluster count:             10
Cluster sizes:             [21, 16, 30, ...]
Distance count:            199
Repetition count:          362
Survival count:            0
```

**What This Means:**
- **Boundary positions:** Indices where residue values change significantly
- **Cluster count:** Number of distinct clusters detected
- **Cluster sizes:** Number of residues in each cluster
- **Distance count:** Number of distance measurements made
- **Repetition count:** Number of repeated residue patterns
- **Survival count:** Number of patterns that survive across segments (single-run: 0 expected)

### Phase 2 Outputs (Multi-Run)

```
THRESHOLD_ONSET — Phase 2 (Multi-Run)

Persistence count:         100
Persistent segments:       99
Repeatability count:       100
Repeatable units:          99
Identity mappings:         99
Identity persistence:      99
Stability count:           47
Stable clusters:           3
```

**What This Means:**
- **Persistence count:** Number of segments that appear in multiple runs
- **Persistent segments:** Segments that survive across runs (hash list, internal)
- **Repeatability count:** Number of units that repeat
- **Repeatable units:** Units that appear multiple times (hash list, internal)
- **Identity mappings:** Segment hash → identity hash mappings (internal)
- **Identity persistence:** Number of identities that persist
- **Stability count:** Number of clusters that are stable across runs
- **Stable clusters:** Clusters that remain consistent (hash list, internal)

### Phase 3 Outputs (Multi-Run)

```
THRESHOLD_ONSET — Phase 3 (Multi-Run)

Node count:                 201
Edge count:                  4851
Total relations:             9857
Persistent relations:        5657
Persistence rate:           0.5739
Stable relations:            5657
Stability ratio:             1.0000
Common edges ratio:          1.0000
Path length count:            9702
```

**What This Means:**
- **Node count:** Number of unique identities in the graph
- **Edge count:** Number of connections between identities
- **Total relations:** Total number of relations detected
- **Persistent relations:** Relations that appear in multiple runs
- **Persistence rate:** Fraction of relations that persist (0.0 to 1.0)
- **Stable relations:** Relations with stable frequencies across runs
- **Stability ratio:** Fraction of persistent relations that are stable (0.0 to 1.0)
- **Common edges ratio:** Fraction of edges that appear in all runs (0.0 to 1.0)
- **Path length count:** Number of paths computed in the graph

### Phase 4 Outputs (Multi-Run)

```
THRESHOLD_ONSET — Phase 4 (Multi-Run)

Identity alias count:         97
Relation alias count:         5831
```

**What This Means:**
- **Identity alias count:** Number of persistent identities that received integer symbols
- **Relation alias count:** Number of persistent relations that received integer symbols

**Note:** Symbol values are never displayed (only counts). Symbols are internal aliases only.

---

## Project Structure

```
THRESHOLD_ONSET/
├── main.py                          # Entry point
├── README.md                        # Basic project overview
├── PROJECT_README.md                # This comprehensive guide
├── requirements.txt                 # Dependencies
│
├── src/                             # Source code
│   ├── phase0/                      # Phase 0 (FROZEN)
│   │   ├── phase0.py                # Core pipeline
│   │   ├── actions.py               # Action variants
│   │   ├── phase0/                  # Phase 0 documentation
│   │   │   └── PHASE0_FREEZE.md     # Freeze declaration
│   │   └── README.md                # Phase 0 overview
│   ├── phase1/                      # Phase 1 (FROZEN)
│   │   ├── phase1.py                # Segmentation pipeline
│   │   ├── boundary.py              # Boundary detection
│   │   ├── cluster.py               # Clustering
│   │   ├── distance.py              # Distance measurement
│   │   ├── pattern.py               # Pattern detection
│   │   ├── phase1/                  # Phase 1 documentation
│   │   │   └── PHASE1_FREEZE.md     # Freeze declaration
│   │   └── README.md                # Phase 1 overview
│   ├── phase2/                      # Phase 2 (FROZEN)
│   │   ├── phase2.py                # Identity pipeline
│   │   ├── persistence.py            # Persistence measurement
│   │   ├── repeatable.py            # Repeatable units
│   │   ├── identity.py              # Identity hashes
│   │   ├── stability.py             # Stability metrics
│   │   ├── phase2/                  # Phase 2 documentation
│   │   │   └── PHASE2_FREEZE.md     # Freeze declaration
│   │   └── README.md                # Phase 2 overview
│   ├── phase3/                      # Phase 3 (FROZEN)
│   │   ├── phase3.py                # Relation pipeline
│   │   ├── relation.py              # Relation extraction
│   │   ├── persistence.py            # Relation persistence
│   │   ├── stability.py             # Relation stability
│   │   ├── graph.py                 # Graph construction
│   │   ├── interaction.py           # Interaction detection
│   │   ├── dependency.py            # Dependency measurement
│   │   ├── influence.py             # Influence metrics
│   │   ├── phase3/                  # Phase 3 documentation
│   │   │   └── PHASE3_FREEZE.md     # Freeze declaration
│   │   └── README.md                # Phase 3 overview
│   ├── phase4/                      # Phase 4 (FROZEN)
│   │   ├── phase4.py                # Symbol pipeline
│   │   ├── alias.py                 # Alias assignment
│   │   ├── phase4/                  # Phase 4 documentation
│   │   │   └── PHASE4_FREEZE.md     # Freeze declaration
│   │   └── README.md                # Phase 4 overview
│   ├── tools/                       # Version control tools
│   │   ├── version_control.py
│   │   ├── watch_version.py
│   │   ├── docs/                    # Tools documentation
│   │   └── README.md                # Tools overview
│   └── README.md                    # Source code overview
│
├── docs/                            # Project documentation
│   ├── axioms/                      # Core design constraints
│   │   ├── AXIOMS.md                # Non-negotiable axioms
│   │   └── README.md
│   ├── architecture/                # System architecture
│   │   ├── ARCHITECTURE.md          # Complete architecture
│   │   └── README.md
│   ├── phase0/                      # Phase 0 documentation
│   ├── phase1/                      # Phase 1 documentation
│   ├── phase2/                      # Phase 2 documentation
│   ├── phase3/                      # Phase 3 documentation
│   ├── phase4/                      # Phase 4 documentation
│   ├── simple/                      # Simple explanations
│   │   ├── PHASE0_TO_PHASE3_STORY.md  # Non-technical story
│   │   ├── INDEPENDENCE_CHECK.md      # Independence analysis
│   │   └── README.md
│   ├── history/                     # Project history
│   │   ├── WORK_LOG.md              # Development log
│   │   ├── CORRECTIONS_APPLIED.md   # Corrections summary
│   │   └── README.md
│   ├── PHASE_STATUS_CANONICAL.md    # Authoritative phase status
│   ├── PHASE_STATUS_ACCURATE.md     # Accurate phase status
│   ├── PHASE_GATES_EXPLANATION.md   # Gate logic explanation
│   ├── EXECUTION_MODES.md           # Execution mode guide
│   └── README.md                    # Documentation overview
│
├── tests/                            # Test suite
│   ├── test_phase3_convergence.py   # Phase 3 convergence test
│   └── test_phase4_freeze.py         # Phase 4 freeze validation
│
├── reference/                       # Reference materials
│   └── README.md
│
├── versions/                        # Version snapshots (auto-generated)
│   └── README.md
│
└── backup_pre_cleanup_20260113/    # Pre-cleanup backups
    └── README.md
```

**Key Directories:**
- `threshold_onset/`: All source code, organized by phase
- `docs/`: Complete documentation, organized by category
- `tests/`: Validation and convergence tests
- `versions/`: Auto-generated version snapshots (if version control enabled)

---

## Documentation Guide

### Core Documentation

- **Axioms:** `docs/axioms/AXIOMS.md` — Non-negotiable design constraints
- **Architecture:** `docs/architecture/ARCHITECTURE.md` — Complete system architecture
- **Phase Status:** `docs/PHASE_STATUS_CANONICAL.md` — Authoritative phase status

### Phase-Specific Documentation

Each phase has:
- **Freeze Declaration:** `threshold_onset/phaseX/phaseX/PHASEX_FREEZE.md` — Immutability record
- **Phase README:** `threshold_onset/phaseX/README.md` — Phase overview and usage

### Simple Explanations

- **Complete Story:** `docs/simple/PHASE0_TO_PHASE3_STORY.md` — Non-technical explanation using analogies
- **Independence Check:** `docs/simple/INDEPENDENCE_CHECK.md` — Analysis of system independence

### Execution Guides

- **Execution Modes:** `docs/EXECUTION_MODES.md` — Single-run vs multi-run mode
- **Phase Gates:** `docs/PHASE_GATES_EXPLANATION.md` — Gate logic and criteria

### Project History

- **Work Log:** `docs/history/WORK_LOG.md` — Development history
- **Corrections:** `docs/history/CORRECTIONS_APPLIED.md` — Corrections summary

**Each directory has its own README.md explaining its contents.**

---

## Testing & Validation

### Phase 3 Convergence Test

**File:** `tests/test_phase3_convergence.py`

**Purpose:** Validates that Phase 3 metrics converge across increasing run counts.

**How to Run:**
```bash
python tests/test_phase3_convergence.py
```

**What It Tests:**
- Gate passes consistently across all run counts
- Stability ratio stays >= threshold (0.6)
- Metrics converge (don't drift significantly)
- No flaky behavior

**Expected Output:**
- Tests with NUM_RUNS = [5, 10, 20]
- All iterations pass
- Stability ratio: 1.0000 (perfect)
- Persistence rate: ~0.82-0.85 (stable)

### Phase 4 Freeze Validation

**File:** `tests/test_phase4_freeze.py`

**Purpose:** Validates Phase 4 freeze-worthiness (determinism, reversibility, immutability, gate determinism).

**How to Run:**
```bash
python tests/test_phase4_freeze.py
```

**What It Tests:**
1. **Determinism:** Same inputs → same alias tables
2. **Gate Determinism:** Gate consistently passes when prerequisites met
3. **Reversibility:** Phase 4 doesn't modify Phase 3 structure
4. **Immutability:** Aliases never change once assigned

**Expected Output:**
- All four tests pass
- Identity alias counts identical across runs
- Relation alias counts identical across runs
- Gate passes 100% of the time

---

## Version Control

THRESHOLD_ONSET includes a local version control system (no Git/GitHub/GitLab required).

### Features

- File watching with `watchfiles`
- Content hashing with SHA256
- SQLite metadata storage
- Unified diffs between versions

### Usage

**Start Version Control:**
```bash
python src/tools/watch_version.py
```

This automatically tracks changes to:
- `src/` directory
- `docs/` directory
- `README.md` and `PROJECT_README.md`

**Version Snapshots:**
- Stored in `versions/` directory
- Auto-generated when files change
- Includes metadata and diffs

**See:** `src/tools/docs/` for detailed version control documentation.

---

## Philosophy & Design Principles

### Core Axiom

**कार्य (kārya) happens before ज्ञान (jñāna)**

Function stabilizes before knowledge appears.

This is not philosophy. This is a design constraint.

### Phase Model

The system follows a strict phase model:

1. **Phase 0:** Action exists without knowledge
2. **Phase 1:** Structure exists without identity
3. **Phase 2:** Identity exists without naming
4. **Phase 3:** Relations exist without naming
5. **Phase 4:** Symbols exist as pure aliases

**Each phase must be frozen before the next can begin.**

### Design Principles

- **No premature naming:** Names come only after structure is proven
- **No interpretation:** System measures structure, not meaning
- **No adaptive thresholds:** All thresholds are fixed and external
- **No learning:** System discovers, does not learn
- **Pure aliasing:** Phase 4 adds zero structure, only reversible aliases

### Why This Matters

Most systems assume you need names first. THRESHOLD_ONSET proves you don't.

**Structure comes before language.**

Just like:
- Your heart beats before you name it "heartbeat"
- Seasons change before you name them "spring/summer"
- Waves crash before you name them "waves"

**Things EXIST and WORK before they get names.**

---

## Common Questions

### Q: Why are all phases frozen?

**A:** Freezing ensures immutability and prevents drift. Each phase is proven correct and locked forever. This maintains the integrity of the foundational architecture.

### Q: Can I modify frozen phases?

**A:** No. Frozen phases are read-only. Modifying them would violate the foundational architecture. If you need different behavior, create a new variant or new phase.

### Q: What if Phase 4 gate fails?

**A:** Gate failure is correct behavior. It means prerequisites aren't met. Check that Phase 3 is frozen and has persistent relations. Gate failure prevents incorrect execution.

### Q: Why integer symbols only?

**A:** Integers are neutral, non-semantic, and non-linguistic. They're the safest possible alias. Letters or tokens would imply ordering, meaning, or language — which Phase 4 must avoid.

### Q: Can I add meaning to symbols?

**A:** No. That would be Phase 5 (or a new project). Phase 4 is pure aliasing. Adding meaning would violate the phase boundaries and the core axiom.

### Q: How do I understand the outputs?

**A:** See the "Understanding Outputs" section above. All outputs are counts, numbers, or internal hashes. There's no interpretation — just structural measurements.

### Q: What's the difference between single-run and multi-run mode?

**A:** Single-run tests repeatability within one sequence. Multi-run tests persistence across independent runs. Multi-run is required for Phase 2 persistence and Phase 3 relations.

### Q: Why are hashes never displayed?

**A:** Hashes are internal identifiers only. Displaying them would imply they have meaning or are names. They're purely structural — like fingerprints, not labels.

---

## Next Steps

### For Users

1. **Run the system:** `python main.py`
2. **Experiment with parameters:** Edit `tokenization_method` and `num_runs` in `integration/run_complete.py`
3. **Test persistence:** Use `num_runs > 1` in `integration/run_complete.py`
4. **Read the story:** `docs/simple/PHASE0_TO_PHASE3_STORY.md`
5. **Explore documentation:** Each directory has a README.md

### For Developers

1. **Understand the axioms:** `docs/axioms/AXIOMS.md`
2. **Study the architecture:** `docs/architecture/ARCHITECTURE.md`
3. **Review freeze declarations:** `threshold_onset/phaseX/phaseX/PHASEX_FREEZE.md`
4. **Run validation tests:** `tests/test_phase3_convergence.py`, `tests/test_phase4_freeze.py`
5. **Respect phase boundaries:** Never modify frozen phases

### For Researchers

1. **Read the independence check:** `docs/simple/INDEPENDENCE_CHECK.md`
2. **Study the phase model:** Each phase proves a specific capability
3. **Examine convergence tests:** Phase 3 and Phase 4 validation
4. **Understand the constraints:** What's allowed vs forbidden in each phase

---

## Support & Resources

### Documentation

- **Complete Guide:** This file (`PROJECT_README.md`)
- **Basic Overview:** `README.md`
- **Simple Story:** `docs/simple/PHASE0_TO_PHASE3_STORY.md`
- **Status:** `docs/PHASE_STATUS_CANONICAL.md`

### Key Files

- **Entry Point:** `main.py`
- **Axioms:** `docs/axioms/AXIOMS.md`
- **Architecture:** `docs/architecture/ARCHITECTURE.md`
- **Freeze Declarations:** `threshold_onset/phaseX/phaseX/PHASEX_FREEZE.md`

### Tests

- **Phase 3 Convergence:** `tests/test_phase3_convergence.py`
- **Phase 4 Freeze Validation:** `tests/test_phase4_freeze.py`

---

## License & Credits

**Project:** THRESHOLD_ONSET

**Core Principle:** कार्य (kārya) happens before ज्ञान (jñāna)

**Status:** All phases (0-4) frozen and complete

**Version:** Foundation complete (2026-01-14)

---

## Final Notes

THRESHOLD_ONSET is a foundational system that proves:

- **Action can exist without knowledge**
- **Structure can exist without identity**
- **Identity can exist without naming**
- **Relations can exist without naming**
- **Symbols can exist as pure aliases**

**All phases are frozen. The foundation is complete.**

**Any work beyond Phase 4 is a new project, not a continuation.**

---

**For detailed information, see README.md files in each directory.**

**For non-technical explanations, see `docs/simple/`.**

**For authoritative status, see `docs/PHASE_STATUS_CANONICAL.md`.**

---

*End of Comprehensive Project Guide*
