# Phase 1 Implementation Prompt (FINAL - CORRECTED)

**Copy this entire prompt and paste it into a new chat session to begin Phase 1 implementation.**

---

```
IMPORTANT: READ CAREFULLY. THIS IS A FOUNDATIONAL SYSTEM.

You are assisting in a project called THRESHOLD_ONSET.

CORE AXIOM (NON-NEGOTIABLE):
कार्य (kārya) happens before ज्ञान (jñāna)
(Function/action stabilizes before knowledge, representation, or meaning.)

PHASE MODEL (STRICT):
The project is divided into phases. You MUST respect phase boundaries.
You are NOT allowed to jump phases, suggest abstractions early, or add interpretation.

PHASE 0 — THRESHOLD_ONSET (FROZEN, DO NOT MODIFY):
Status: ✅ FROZEN PERMANENTLY
- Implemented, verified, complete
- Cannot be modified
- Must NOT be altered or extended

Purpose:
- Prove that action can exist without knowledge.

Allowed in Phase 0:
- Action
- Opaque residue / trace
- Repetition
- Persistence
- Survival (count-based only)

Forbidden in Phase 0:
- Symbols, labels, names, IDs, meaning, interpretation
- Segmentation, distributions, visualization
- Statistics beyond counts, min/max, ranges, bins
- Real-time narration, plots, coordinates

Canonical Phase 0 Output (ONLY):
- Total residue count
- Unique residue count
- Collision rate
Nothing else.

Phase 0 Implementation:
- Location: `src/phase0/phase0.py`
- Function: `phase0(actions, steps)` - yields (trace, count, step_count)
- Main entry: `main.py` - calls `run_phase0()` which returns list of residues
- Residues are: float values from `random.random()` (0.0 to 1.0, exclusive)
- Structureless, opaque, no meaning
- Returns: Opaque residue list (internal handoff to Phase 1 only; not to be inspected or displayed)

CURRENT TASK: IMPLEMENT PHASE 1 — SEGMENTATION

PHASE 1 — SEGMENTATION (TO BE IMPLEMENTED):
Core Question:
- When does raw, opaque residue become separable into distinguishable parts?

Phase 1 Definition:
- Segmentation WITHOUT naming
- Boundary detection WITHOUT identity
- Differences WITHOUT symbols
- Clustering WITHOUT labels
- Pattern detection WITHOUT interpretation

What Phase 1 Allows (New Capabilities):
1. Boundary Detection
   - Detect where one residue differs from another
   - Identify separation points
   - Find discontinuities
   - Return: boundary positions (indices only)
   - NOT allowed: Name boundaries, label them, interpret them
   - CONSTRAINT: Thresholds must be FIXED, EXTERNAL, and NON-ADAPTIVE.
     No learning, tuning, or optimization allowed in Phase 1.

2. Difference Measurement
   - Compute distance between residues
   - Measure similarity/dissimilarity
   - Quantify separation
   - Return: distance measurements (raw numbers)
   - NOT allowed: Classify differences, name types of differences
   - CONSTRAINT: Distance metrics must be mechanically defined (e.g., absolute difference).
     No adaptive or learned metrics.

3. Clustering
   - Group residues by proximity
   - Identify clusters
   - Count cluster sizes
   - Return: cluster counts, cluster size counts (unordered, no distribution)
   - NOT allowed: Name clusters, label groups, interpret clusters
   - CONSTRAINT: Clustering thresholds must be FIXED and EXTERNAL.
     No adaptive clustering or optimization.

4. Pattern Detection
   - Detect repetition in residue sequences
   - Identify recurring structures
   - Find invariants under transformation
   - Return: repetition counts, survival counts (numbers only)
   - NOT allowed: Name patterns, interpret meaning, assign symbols
   - CONSTRAINT: Pattern detection limited to EXACT EQUALITY or FIXED-WINDOW comparison.
     No abstraction, compression, or symbolic patterning allowed.

5. Structural Metrics
   - Cluster count
   - Cluster size counts (unordered, no distribution interpretation)
   - Separation distances (raw numbers)
   - Boundary positions (indices only)
   - NOT allowed: Min/max interpretation, statistical analysis beyond counts, distribution interpretation

What Phase 1 Forbids (Still Not Allowed):
- ❌ Symbols, labels, names, IDs
- ❌ Meaning, interpretation, semantic analysis
- ❌ Classification, categorization
- ❌ Tokenization, embeddings
- ❌ Visualization (plots, coordinates)
- ❌ Statistical analysis (beyond counts)
- ❌ Min/max interpretation, range interpretation, distribution interpretation
- ❌ Adaptive thresholds, learning, tuning, optimization
- ❌ Real-time logs, stepwise narration, temporal displays
- ❌ Pattern abstraction, compression, symbolic patterning

Phase 1 Implementation Constraints:
1. Phase 0 Remains Frozen
   - Phase 0 code cannot be modified
   - Phase 0 output format cannot change
   - Phase 1 reads Phase 0 output only

2. No Backward Contamination
   - Phase 1 cannot add features to Phase 0
   - Phase 1 operates as separate layer
   - Phase 0 constraints remain enforced

3. Minimal Interface
   - Phase 1 receives: residue list (opaque floats from Phase 0)
   - Phase 1 returns: structural metrics (numbers/indices only)
   - No shared state with Phase 0

4. Test-Driven Transition
   - Phase 1 begins only when tests pass
   - Tests must be minimal and verifiable
   - No transition without test validation

5. Fixed Thresholds Only
   - All thresholds must be FIXED, EXTERNAL, and NON-ADAPTIVE
   - No learning, tuning, optimization, or adaptive selection
   - Thresholds defined as constants, not computed from data

6. Exact Comparisons Only
   - Pattern detection uses EXACT EQUALITY or FIXED-WINDOW comparison
   - No abstraction, compression, or symbolic patterning
   - No approximate matching or fuzzy comparison

Phase 1 Structure (Required):
```
src/phase1/
  - boundary.py    - Boundary detection (indices only)
  - cluster.py     - Clustering (counts only)
  - distance.py    - Distance measurement (raw numbers)
  - pattern.py     - Pattern detection (counts only)
  - phase1.py      - Phase 1 pipeline (segmentation without naming)
```

Each component:
- Operates on opaque residues (from Phase 0)
- Returns only numbers/indices
- No naming, no interpretation
- Enforces segmentation without symbols
- Reads Phase 0 output, does not modify Phase 0
- Uses FIXED thresholds only (no adaptation)
- Uses EXACT comparisons only (no abstraction)

Minimal Tests for Segmentation Emergence:

Test 1: Boundary Detection
- Compare consecutive residues
- Compute difference metric (raw number, e.g., absolute difference)
- Identify positions where difference exceeds FIXED threshold
- Return: boundary positions (indices only)
- Pass: Boundaries detected, no labels, only indices returned
- CONSTRAINT: Threshold must be FIXED and EXTERNAL (not computed from data)

Test 2: Clustering
- Compute pairwise distances (raw numbers, e.g., absolute difference)
- Group residues within FIXED distance threshold
- Count groups
- Return: group counts, group size counts (unordered, no distribution)
- Pass: Groups identified, no group names, only counts returned
- CONSTRAINT: Distance threshold must be FIXED and EXTERNAL

Test 3: Pattern Repetition
- Compare residue subsequences using EXACT EQUALITY
- Detect exact matches (raw comparison, no abstraction)
- Count repetition frequency
- Return: repetition count (number only)
- Pass: Repetitions detected, no pattern names, only counts returned
- CONSTRAINT: Only EXACT equality allowed. No approximate matching.

Test 4: Structural Invariance
- Track residue sequences across iterations
- Identify sequences that survive using EXACT EQUALITY
- Count survival frequency
- Return: survival counts (numbers only)
- Pass: Invariants identified, no structure names, only counts returned
- CONSTRAINT: Only EXACT equality allowed. No pattern abstraction.

Phase 1 Output Specification:
Allowed Output:
- Boundary positions (indices)
- Cluster counts
- Cluster size counts (unordered list, no distribution interpretation)
- Distance measurements (raw numbers)
- Repetition counts
- Survival counts
- Separation metrics (raw numbers)

Forbidden Output:
- Cluster names, boundary labels, pattern names, structure names
- Interpretations, classifications, meanings
- Distributions, statistical summaries, min/max interpretations
- Real-time logs, stepwise narration, temporal displays
- Adaptive thresholds, learned parameters

Implementation Requirements:
1. Create `src/phase1/` directory structure
2. Implement each component (boundary, cluster, distance, pattern, phase1)
3. Each component must:
   - Accept Phase 0 residues as input (list of floats)
   - Return only numbers/indices (no names, no labels)
   - Operate on opaque residues (no interpretation)
   - Enforce segmentation without naming
   - Use FIXED thresholds only (defined as constants)
   - Use EXACT comparisons only (no abstraction)
4. Create `main.py` integration that:
   - Runs Phase 0 to get residues
   - Passes residues to Phase 1
   - Displays FINAL Phase 1 outputs only (no stepwise or temporal logs)
5. Ensure NO modification to Phase 0 code
6. Ensure NO naming, labeling, or interpretation in Phase 1
7. Ensure NO adaptive thresholds, learning, or optimization
8. Ensure NO real-time logs, stepwise narration, or temporal displays

Code Style:
- Python standard library only (no third-party modules except version control)
- Clean, minimal code
- Clear docstrings explaining constraints
- No violation of phase boundaries
- All thresholds defined as FIXED constants
- All comparisons use EXACT equality

DO NOT:
- Modify Phase 0 code
- Add names, labels, or symbols to Phase 1
- Interpret or classify residues
- Use visualization, plots, or coordinates
- Add meaning or semantics
- Jump to Phase 2 concepts (identity, naming)
- Explain philosophy - just implement constraints
- Use adaptive thresholds, learning, or optimization
- Create real-time logs, stepwise narration, or temporal displays
- Use pattern abstraction, compression, or symbolic patterning
- Interpret distributions, statistical summaries, or min/max values

If you violate phase boundaries, you are wrong.
If you explain instead of constrain, you are wrong.
If you add interpretation, you are wrong.
If you use adaptive thresholds, you are wrong.
If you create real-time logs, you are wrong.

Proceed carefully. Implement Phase 1 segmentation without naming.
```

---

**End of Prompt (FINAL - CORRECTED)**
