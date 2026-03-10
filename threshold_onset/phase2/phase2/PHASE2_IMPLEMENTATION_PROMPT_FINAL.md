# Phase 2 Implementation Prompt (FINAL)

**Copy this entire prompt and paste it into a new chat session to begin Phase 2 implementation.**

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
- Returns: Opaque residue list (internal handoff to Phase 1 only)

PHASE 1 — SEGMENTATION (FROZEN, DO NOT MODIFY):
Status: ✅ FROZEN PERMANENTLY
- Implemented, verified, complete
- Cannot be modified
- Must NOT be altered or extended

Purpose:
- Segmentation without naming
- Boundary detection, clustering, pattern detection
- Returns structural metrics only (numbers/indices)

Phase 1 Implementation:
- Location: `src/phase1/phase1.py`
- Function: `phase1(residues)` - returns structural metrics dictionary
- Components: boundary.py, cluster.py, distance.py, pattern.py
- Output: Dictionary with boundary_positions, cluster_count, cluster_sizes, distances, repetition_count, survival_count
- All metrics are numbers/indices only (no names, no labels)

CURRENT TASK: IMPLEMENT PHASE 2 — IDENTITY

PHASE 2 — IDENTITY (TO BE IMPLEMENTED):
Core Question:
- When does a segment persist enough to deserve an identity?

Phase 2 Definition:
- Identity WITHOUT naming
- Persistence measurement WITHOUT meaning
- Repeatable units WITHOUT symbols
- Stable clusters WITHOUT labels
- Identity hashes (internal only, not symbolic)

What Phase 2 Allows (New Capabilities):
1. Persistence Measurement
   - Measure how long segments/clusters persist across iterations
   - Track stability of structures
   - Count persistence frequency
   - Return: persistence counts, stability metrics (numbers only)
   - NOT allowed: Name persistent structures, label them, interpret meaning

2. Repeatable Unit Detection
   - Identify segments that repeat across different contexts
   - Detect units that appear consistently
   - Count repeatability frequency
   - Return: repeatability counts, unit frequencies (numbers only)
   - NOT allowed: Name units, assign symbols, create labels

3. Identity Hash Generation
   - Generate internal identity hashes for persistent segments
   - Create hash-based identifiers (internal only)
   - Map segments to hash values
   - Return: hash mappings (hash values only, no symbolic names)
   - NOT allowed: Use hashes as names, assign meaning to hashes, create symbolic labels

4. Stability Metrics
   - Measure stability of clusters across iterations
   - Track cluster persistence
   - Count stable cluster occurrences
   - Return: stability counts, persistence metrics (numbers only)
   - NOT allowed: Name stable clusters, interpret stability, assign meaning

5. Identity Assignment (Internal Only)
   - Assign internal identity hashes to persistent segments
   - Create identity mappings (hash-based)
   - Track identity persistence
   - Return: identity mappings (hash values only)
   - NOT allowed: Use identities as names, create symbolic labels, assign meaning

What Phase 2 Forbids (Still Not Allowed):
- ❌ Symbolic naming (names, labels, symbols)
- ❌ Linguistic labels (words, tokens, letters)
- ❌ Meaning, interpretation, semantic analysis
- ❌ Classification, categorization with names
- ❌ Tokenization, embeddings
- ❌ Visualization (plots, coordinates)
- ❌ Statistical analysis (beyond counts)
- ❌ Adaptive thresholds, learning, optimization
- ❌ Real-time logs, stepwise narration
- ❌ Pattern abstraction beyond exact equality
- ❌ Using identity hashes as names or symbols

Phase 2 Implementation Constraints:
1. Phase 0 and Phase 1 Remain Frozen
   - Phase 0 code cannot be modified
   - Phase 1 code cannot be modified
   - Phase 2 reads Phase 0 and Phase 1 output only
   - No backward contamination

2. No Backward Contamination
   - Phase 2 cannot add features to Phase 0 or Phase 1
   - Phase 2 operates as separate layer
   - Phase 0 and Phase 1 constraints remain enforced

3. Minimal Interface
   - Phase 2 receives: Phase 0 residues + Phase 1 metrics
   - Phase 2 returns: Identity metrics (hashes and counts only)
   - No shared state with Phase 0 or Phase 1

4. Test-Driven Transition
   - Phase 2 begins only when tests pass
   - Tests must be minimal and verifiable
   - No transition without test validation

5. Fixed Thresholds Only
   - All thresholds must be FIXED, EXTERNAL, and NON-ADAPTIVE
   - No learning, tuning, optimization, or adaptive selection
   - Thresholds defined as constants, not computed from data

6. Exact Comparisons Only
   - Identity detection uses EXACT EQUALITY or FIXED-WINDOW comparison
   - No abstraction, compression, or symbolic patterning
   - No approximate matching or fuzzy comparison

7. Identity Hashes Are Internal Only
   - Hashes are for internal tracking only
   - Hashes are NOT names, labels, or symbols
   - Hashes are NOT to be displayed as names
   - Hashes are mechanical identifiers, not meaningful labels

Phase 2 Structure (Required):
```
src/phase2/
  - persistence.py   - Persistence measurement (counts only)
  - repeatable.py    - Repeatable unit detection (counts only)
  - identity.py      - Identity hash generation (hashes only, internal)
  - stability.py     - Stability metrics (counts only)
  - phase2.py        - Phase 2 pipeline (identity without naming)
```

Each component:
- Operates on Phase 0 residues and Phase 1 metrics
- Returns only numbers/hashes (no names, no labels)
- No naming, no interpretation
- Enforces identity without symbolic naming
- Reads Phase 0/Phase 1 output, does not modify them
- Uses FIXED thresholds only (no adaptation)
- Uses EXACT comparisons only (no abstraction)

Minimal Tests for Identity Emergence:

Test 1: Persistence Detection
- Track segments across multiple Phase 0 iterations
- Count how many times each segment appears
- Identify segments that persist above threshold
- Return: persistence counts, persistent segment hashes (numbers/hashes only)
- Pass: Persistence detected, no names, only counts/hashes returned
- CONSTRAINT: Threshold must be FIXED and EXTERNAL

Test 2: Repeatable Unit Detection
- Compare segments across different contexts
- Detect units that repeat consistently
- Count repeatability frequency
- Return: repeatability counts, unit hashes (numbers/hashes only)
- Pass: Repeatable units identified, no unit names, only counts/hashes returned
- CONSTRAINT: Only EXACT equality allowed

Test 3: Identity Hash Assignment
- Generate hash-based identities for persistent segments
- Create identity mappings (hash to segment)
- Track identity persistence
- Return: identity mappings (hash values only, no names)
- Pass: Identities assigned, no symbolic names, only hashes returned
- CONSTRAINT: Hashes are internal only, not symbolic

Test 4: Stability Measurement
- Measure cluster stability across iterations
- Track which clusters persist
- Count stability frequency
- Return: stability counts, stable cluster hashes (numbers/hashes only)
- Pass: Stability measured, no cluster names, only counts/hashes returned
- CONSTRAINT: Only EXACT equality allowed

Phase 2 Output Specification:
Allowed Output:
- Persistence counts (numbers)
- Repeatability counts (numbers)
- Identity hashes (hash values, internal only)
- Stability counts (numbers)
- Identity mappings (hash to segment, no names)
- Persistent segment hashes (hash values only)

Forbidden Output:
- Segment names, cluster names, unit names
- Symbolic labels, linguistic labels
- Interpretations, classifications with names
- Meanings, semantic analysis
- Using hashes as names or symbols
- Displaying hashes as meaningful labels

Implementation Requirements:
1. Create `src/phase2/` directory structure
2. Implement each component (persistence, repeatable, identity, stability, phase2)
3. Each component must:
   - Accept Phase 0 residues and Phase 1 metrics as input
   - Return only numbers/hashes (no names, no labels)
   - Operate on opaque data (no interpretation)
   - Enforce identity without symbolic naming
   - Use FIXED thresholds only
   - Use EXACT comparisons only
4. Create `main.py` integration that:
   - Runs Phase 0 to get residues
   - Runs Phase 1 on residues
   - Runs Phase 2 on residues + Phase 1 metrics
   - Displays FINAL Phase 2 outputs only (no stepwise or temporal logs)
5. Ensure NO modification to Phase 0 or Phase 1 code
6. Ensure NO naming, labeling, or symbolic interpretation in Phase 2
7. Ensure identity hashes are INTERNAL ONLY (not displayed as names)

Code Style:
- Python standard library only (no third-party modules except version control)
- Clean, minimal code
- Clear docstrings explaining constraints
- No violation of phase boundaries
- All thresholds defined as FIXED constants
- All comparisons use EXACT equality
- Identity hashes are internal tracking only

DO NOT:
- Modify Phase 0 or Phase 1 code
- Add names, labels, or symbols to Phase 2
- Interpret or classify with names
- Use visualization, plots, or coordinates
- Add meaning or semantics
- Use identity hashes as names or symbols
- Display hashes as meaningful labels
- Jump to Phase 3 concepts (relations, graphs)
- Explain philosophy - just implement constraints
- Use adaptive thresholds, learning, or optimization
- Create real-time logs, stepwise narration, or temporal displays

If you violate phase boundaries, you are wrong.
If you explain instead of constrain, you are wrong.
If you add interpretation, you are wrong.
If you use hashes as names, you are wrong.
If you create real-time logs, you are wrong.

Proceed carefully. Implement Phase 2 identity without naming.
```

---

**End of Prompt (FINAL)**
