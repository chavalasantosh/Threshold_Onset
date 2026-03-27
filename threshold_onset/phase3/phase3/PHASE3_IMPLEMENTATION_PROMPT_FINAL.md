# Phase 3 Implementation Prompt (FINAL)

**Copy this entire prompt and paste it into a new chat session to begin Phase 3 implementation.**

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

PHASE 2 — IDENTITY (FROZEN, DO NOT MODIFY):
Status: ✅ FROZEN PERMANENTLY
- Implemented, verified, complete
- Cannot be modified
- Must NOT be altered or extended

Purpose:
- Identity without naming
- Persistence measurement, repeatable units, identity hashes (internal only)
- Returns identity metrics only (hashes and counts)

Phase 2 Implementation:
- Location: `src/phase2/phase2.py`
- Function: `phase2(residues, phase1_metrics)` - returns identity metrics dictionary
- Components: persistence.py, repeatable.py, identity.py, stability.py
- Output: Dictionary with persistence_counts, persistent_segment_hashes, repeatability_counts, repeatable_unit_hashes, identity_mappings, identity_persistence, stability_counts, stable_cluster_hashes
- All metrics are hashes and counts only (no names, no labels)
- Identity hashes are INTERNAL ONLY (not displayed as names)

CURRENT TASK: IMPLEMENT PHASE 3 — RELATION

PHASE 3 — RELATION (TO BE IMPLEMENTED):
Core Question:
- How do identities influence one another?

Phase 3 Definition:
- Relations WITHOUT naming
- Graph structures WITHOUT symbolic labels
- Interactions WITHOUT meaning
- Dependencies WITHOUT interpretation
- Influence measurement WITHOUT semantics

What Phase 3 Allows (New Capabilities):
1. Graph Structure Construction
   - Build graph structures from identities
   - Create nodes from identity hashes (internal identifiers only)
   - Create edges from relations between identities
   - Return: graph structure (nodes and edges as hash pairs, no names)
   - NOT allowed: Name nodes, label edges, interpret graph structure

2. Interaction Detection
   - Detect when identities appear together
   - Identify co-occurrence patterns
   - Measure interaction frequency
   - Return: interaction counts, co-occurrence pairs (hash pairs only)
   - NOT allowed: Name interactions, label patterns, interpret meaning

3. Dependency Measurement
   - Measure dependencies between identities
   - Track which identities depend on others
   - Count dependency frequency
   - Return: dependency counts, dependency pairs (hash pairs only)
   - NOT allowed: Name dependencies, label relationships, interpret structure

4. Influence Metrics
   - Measure how identities influence each other
   - Track influence strength (raw numbers)
   - Count influence frequency
   - Return: influence counts, influence strengths (numbers only)
   - NOT allowed: Name influences, label relationships, interpret meaning

5. Graph Metrics
   - Node count (number of identities in graph)
   - Edge count (number of relations)
   - Degree counts (connection counts per node)
   - Path lengths (raw numbers)
   - NOT allowed: Node names, edge labels, path interpretation, graph visualization

What Phase 3 Forbids (Still Not Allowed):
- ❌ Symbolic naming (names, labels, symbols)
- ❌ Linguistic labels (words, tokens, letters)
- ❌ Meaning, interpretation, semantic analysis
- ❌ Classification, categorization with names
- ❌ Using identity hashes as names or symbols
- ❌ Graph visualization (plots, coordinates, visual graphs)
- ❌ Node labels, edge labels, path names
- ❌ Statistical analysis (beyond counts)
- ❌ Adaptive thresholds, learning, optimization
- ❌ Real-time logs, stepwise narration
- ❌ Pattern abstraction beyond exact equality
- ❌ Displaying graph structures with names or labels

Phase 3 Implementation Constraints:
1. Phase 0, Phase 1, and Phase 2 Remain Frozen
   - Phase 0 code cannot be modified
   - Phase 1 code cannot be modified
   - Phase 2 code cannot be modified
   - Phase 3 reads Phase 0, Phase 1, and Phase 2 output only
   - No backward contamination

2. No Backward Contamination
   - Phase 3 cannot add features to Phase 0, Phase 1, or Phase 2
   - Phase 3 operates as separate layer
   - Phase 0, Phase 1, and Phase 2 constraints remain enforced

3. Minimal Interface
   - Phase 3 receives: Phase 0 residues + Phase 1 metrics + Phase 2 metrics
   - Phase 3 returns: Relation metrics (graph structures, counts, hash pairs only)
   - No shared state with previous phases

4. Test-Driven Transition
   - Phase 3 begins only when tests pass
   - Tests must be minimal and verifiable
   - No transition without test validation

5. Fixed Thresholds Only
   - All thresholds must be FIXED, EXTERNAL, and NON-ADAPTIVE
   - No learning, tuning, optimization, or adaptive selection
   - Thresholds defined as constants, not computed from data

6. Exact Comparisons Only
   - Relation detection uses EXACT EQUALITY or FIXED-WINDOW comparison
   - No abstraction, compression, or symbolic patterning
   - No approximate matching or fuzzy comparison

7. Graph Structures Are Internal Only
   - Graphs use identity hashes as node identifiers (internal only)
   - Edges are hash pairs (internal identifiers only)
   - Graphs are NOT to be displayed with names or labels
   - Graphs are structural representations, not symbolic networks

Phase 3 Structure (Required):
```
src/phase3/
  - graph.py        - Graph structure construction (hash pairs only)
  - interaction.py  - Interaction detection (counts and hash pairs)
  - dependency.py    - Dependency measurement (counts and hash pairs)
  - influence.py     - Influence metrics (numbers only)
  - phase3.py        - Phase 3 pipeline (relation without naming)
```

Each component:
- Operates on Phase 0 residues, Phase 1 metrics, and Phase 2 metrics
- Returns only numbers/hash pairs (no names, no labels)
- No naming, no interpretation
- Enforces relation without symbolic naming
- Reads Phase 0/Phase 1/Phase 2 output, does not modify them
- Uses FIXED thresholds only (no adaptation)
- Uses EXACT comparisons only (no abstraction)

Minimal Tests for Relation Emergence:

Test 1: Graph Structure Construction
- Build graph from identity hashes
- Create nodes from identity hashes (internal identifiers)
- Create edges from co-occurrence or dependency
- Return: graph structure (nodes as hash set, edges as hash pairs)
- Pass: Graph constructed, no node names, no edge labels, only hash structures
- CONSTRAINT: Threshold must be FIXED and EXTERNAL

Test 2: Interaction Detection
- Detect when identity hashes appear together
- Count interaction frequency
- Identify interaction pairs
- Return: interaction counts, interaction pairs (hash pairs only)
- Pass: Interactions detected, no interaction names, only hash pairs returned
- CONSTRAINT: Only EXACT equality allowed

Test 3: Dependency Measurement
- Measure dependencies between identity hashes
- Track dependency relationships
- Count dependency frequency
- Return: dependency counts, dependency pairs (hash pairs only)
- Pass: Dependencies measured, no dependency names, only hash pairs returned
- CONSTRAINT: Only EXACT equality allowed

Test 4: Influence Metrics
- Measure influence strength between identities
- Track influence frequency
- Count influence occurrences
- Return: influence counts, influence strengths (numbers only)
- Pass: Influence measured, no influence names, only numbers returned
- CONSTRAINT: Only EXACT equality allowed

Phase 3 Output Specification:
Allowed Output:
- Graph structure (nodes as hash set, edges as hash pairs)
- Node count (number)
- Edge count (number)
- Degree counts (dict mapping node hash to degree count)
- Interaction counts (dict mapping hash pair to count)
- Dependency counts (dict mapping hash pair to count)
- Influence counts (dict mapping hash pair to count)
- Influence strengths (dict mapping hash pair to raw number)
- Path lengths (raw numbers)

Forbidden Output:
- Node names, edge labels, path names
- Graph visualization, plots, coordinates
- Symbolic labels, linguistic labels
- Interpretations, classifications with names
- Meanings, semantic analysis
- Using hashes as names or symbols
- Displaying graph structures with names or labels

Implementation Requirements:
1. Create `src/phase3/` directory structure
2. Implement each component (graph, interaction, dependency, influence, phase3)
3. Each component must:
   - Accept Phase 0 residues, Phase 1 metrics, and Phase 2 metrics as input
   - Return only numbers/hash pairs (no names, no labels)
   - Operate on opaque data (no interpretation)
   - Enforce relation without symbolic naming
   - Use FIXED thresholds only (defined as constants)
   - Use EXACT comparisons only (no abstraction)
4. Create `main.py` integration that:
   - Runs Phase 0 to get residues
   - Runs Phase 1 on residues
   - Runs Phase 2 on residues + Phase 1 metrics
   - Runs Phase 3 on residues + Phase 1 metrics + Phase 2 metrics
   - Displays FINAL Phase 3 outputs only (no stepwise or temporal logs)
5. Ensure NO modification to Phase 0, Phase 1, or Phase 2 code
6. Ensure NO naming, labeling, or symbolic interpretation in Phase 3
7. Ensure graph structures use hashes only (not displayed as names)
8. Ensure NO graph visualization (plots, coordinates, visual graphs)

Code Style:
- Python standard library only (no third-party modules except version control)
- Clean, minimal code
- Clear docstrings explaining constraints
- No violation of phase boundaries
- All thresholds defined as FIXED constants
- All comparisons use EXACT equality
- Graph structures use identity hashes as internal identifiers only

DO NOT:
- Modify Phase 0, Phase 1, or Phase 2 code
- Add names, labels, or symbols to Phase 3
- Interpret or classify with names
- Use visualization, plots, or coordinates
- Add meaning or semantics
- Use identity hashes as names or symbols
- Display graph structures with names or labels
- Create graph visualizations
- Jump to Phase 4 concepts (symbols, letters, tokens)
- Explain philosophy - just implement constraints
- Use adaptive thresholds, learning, or optimization
- Create real-time logs, stepwise narration, or temporal displays

If you violate phase boundaries, you are wrong.
If you explain instead of constrain, you are wrong.
If you add interpretation, you are wrong.
If you use hashes as names, you are wrong.
If you create graph visualizations, you are wrong.
If you create real-time logs, you are wrong.

Proceed carefully. Implement Phase 3 relation without naming.
```

---

**End of Prompt (FINAL)**
