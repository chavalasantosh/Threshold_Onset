# Phase 3 Completion Implementation Prompt

**Date:** 2026-01-13  
**Status:** 📋 **READY FOR IMPLEMENTATION**

---

## Context

Phase 3 currently **executes and produces metrics** but does **NOT test persistence** and does **NOT have freeze criteria**.

This prompt implements Phase 3 persistence testing, stability measurement, and gate logic to make Phase 3 **complete and freezable**.

---

## Core Requirements

1. **Relation Hash Definition**: Structural relation signatures (hash-only, no names)
2. **Multi-Run Collection**: Collect relations across multiple independent Phase 0 runs
3. **Persistence Testing**: Relations must appear in ≥ 2 runs to be persistent
4. **Stability Measurement**: Numerical stability metrics (variance, ratios)
5. **Gate Logic**: Phase 3 must refuse execution if criteria not met
6. **Freeze Criteria**: Phase 3 can only freeze when relations persist and stabilize

---

## Implementation Tasks

### Task 1: Relation Hash Generation

**File:** `src/phase3/relation.py`

**Function:** `generate_relation_hash(source_hash, target_hash, relation_type_hash)`

**Purpose:** Generate hash-based relation identifier.

**Implementation:**
- Combine source_hash, target_hash, relation_type_hash
- Hash using SHA256 (internal identifier only)
- Return relation_hash (string)

**Function:** `extract_relations(phase3_metrics)`

**Purpose:** Extract all relations from Phase 3 metrics and generate relation_hashes.

**Implementation:**
- Extract interaction_pairs, dependency_pairs, influence_counts from phase3_metrics
- For each pair, generate relation_hash
- Return: `{'relation_hashes': set, 'relation_counts': dict}`

**Fixed Constants (CRITICAL - Must be global, not derived dynamically):**
```python
# These must be computed once at module level, not per-call
# This avoids "relation drift" and ensures consistency across runs
INTERACTION_TYPE_HASH = hashlib.sha256(b"interaction").hexdigest()
DEPENDENCY_TYPE_HASH = hashlib.sha256(b"dependency").hexdigest()
INFLUENCE_TYPE_HASH = hashlib.sha256(b"influence").hexdigest()
```

---

### Task 2: Relation Persistence Measurement

**File:** `src/phase3/persistence.py`

**Function:** `measure_relation_persistence(relation_hashes_per_run, threshold=RELATION_PERSISTENCE_THRESHOLD)`

**Purpose:** Measure which relations persist across multiple runs.

**Fixed Threshold:**
```python
RELATION_PERSISTENCE_THRESHOLD = 2  # Minimum runs for persistence
```

**Implementation:**
- Count how many runs contain each relation_hash
- Mark as persistent if count ≥ threshold
- Compute persistence_rate = persistent_relations / total_relations

**Returns:**
- `persistence_counts`: Dict mapping relation_hash to persistence count
- `persistent_relation_hashes`: Set of persistent relation hashes
- `persistence_rate`: Float (0.0 to 1.0)

---

### Task 3: Relation Stability Measurement

**File:** `src/phase3/stability.py`

**Function:** `measure_relation_stability(relation_hashes_per_run, relation_counts_per_run, graph_metrics_per_run, persistent_relation_hashes)`

**Purpose:** Measure numerical stability of relations across runs.

**CRITICAL:** Stability is **secondary to persistence**, not parallel.
- Input `persistent_relation_hashes` (already filtered from persistence step)
- Measure stability **only on persistent relations**
- Do **NOT** compute stability on transient relations

**Fixed Thresholds:**
```python
STABILITY_VARIANCE_THRESHOLD = 2.0  # Maximum variance for stable relations
STABILITY_RATIO_THRESHOLD = 0.6     # Minimum ratio for stable graph
```

**Implementation:**
- For each persistent relation_hash:
  - Count occurrences in each run
  - Compute variance of occurrence counts
  - Mark as stable if variance ≤ threshold
- Compute edge density for each run: edge_count / node_count
- Compute variance of edge density
- Compute common_edges_ratio: intersection of graph_edges across runs

**Returns:**
- `stability_counts`: Dict mapping relation_hash to stability count
- `stable_relation_hashes`: Set of stable relation hashes
- `stability_ratio`: Float (0.0 to 1.0)
- `edge_density_variance`: Float
- `common_edges_ratio`: Float (0.0 to 1.0)

---

### Task 4: Multi-Run Phase 3 Pipeline

**File:** `src/phase3/phase3.py` (UPDATE)

**Function:** `phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)`

**Purpose:** Run Phase 3 across multiple runs and compute persistence/stability.

**Implementation:**
1. For each run:
   - Call `phase3(residues, phase1_metrics, phase2_metrics)`
   - Extract relations using `extract_relations()`
   - Store relation_hashes and relation_counts
2. Aggregate relations across all runs
3. Measure persistence using `measure_relation_persistence()`
4. Measure stability using `measure_relation_stability()`
5. Build aggregated graph (union of all graph_nodes and graph_edges)
6. Apply gate logic (see Task 5)
7. Return complete relation metrics

**Returns:** Dictionary with all relation metrics (see PHASE3_PERSISTENCE.md for full contract)

---

### Task 5: Phase 3 Gate Logic

**File:** `src/phase3/phase3.py` (UPDATE)

**Function:** `_check_phase3_gate(phase2_metrics, persistent_relations, stability_ratio)`

**Purpose:** Check if Phase 3 gate criteria are met.

**Fixed Thresholds:**
```python
MIN_PERSISTENT_RELATIONS = 1        # Minimum persistent relations required
MIN_STABILITY_RATIO = 0.6           # Minimum stability ratio required
```

**Gate Criteria:**
1. Phase 2 produced persistent identities:
   - `len(phase2_metrics.get('persistent_segment_hashes', [])) > 0` OR
   - `len(phase2_metrics.get('identity_mappings', {})) > 0`
2. Persistent relations exist:
   - `persistent_relations >= MIN_PERSISTENT_RELATIONS`
3. Stability threshold met:
   - `stability_ratio >= MIN_STABILITY_RATIO`

**Returns:** `True` if gate passes, `False` if gate fails

**If gate fails:**
- Return `None` from `phase3_multi_run()`
- Do not compute or return relation metrics

---

### Task 6: Main Integration

**File:** `main.py` (UPDATE)

**Function:** `run_phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)`

**Purpose:** Run Phase 3 multi-run pipeline from main.py.

**Implementation:**
- Call `phase3_multi_run()` from phase3.phase3
- Check if result is `None` (gate failed)
- If gate failed, print gate failure message and return `None`
- If gate passed, print Phase 3 results and return metrics

**Update:** `if __name__ == "__main__":` block
- In multi-run mode, call `run_phase3_multi_run()` instead of `run_phase3()`
- Pass all required parameters

---

## Constraints (CRITICAL)

### Must NOT Do:
- ❌ Modify Phase 0, Phase 1, or Phase 2 code
- ❌ Add names, labels, or symbols to relations
- ❌ Visualize graphs (plots, coordinates, visual graphs)
- ❌ Interpret or classify relations with names
- ❌ Use adaptive thresholds, learning, or optimization
- ❌ Display relation hashes as names or symbols
- ❌ Create real-time logs or stepwise narration

### Must Do:
- ✅ Use fixed thresholds only (defined as constants)
- ✅ Use exact equality for hash comparison
- ✅ Return only numbers/hash pairs (no names, no labels)
- ✅ Graph structures are internal only (not displayed)
- ✅ All hashes are internal identifiers only
- ✅ Output shows only counts/lengths (no hash values displayed)

---

## Testing Strategy

1. **Test Relation Hash Generation:**
   - Generate relation_hash from source, target, type
   - Verify same inputs produce same hash
   - Verify different inputs produce different hashes

2. **Test Persistence:**
   - Run Phase 3 on 5 independent runs
   - Verify relations appearing in ≥ 2 runs are marked persistent
   - Verify persistence_rate is computed correctly

3. **Test Stability:**
   - Run Phase 3 on multiple runs with consistent relations
   - Verify stability_ratio ≥ 0.6 when relations are stable
   - Verify variance calculations are correct

4. **Test Gate:**
   - Test gate with no persistent identities → should fail
   - Test gate with persistent identities but no persistent relations → should fail
   - Test gate with persistent relations but low stability → should fail
   - Test gate with all criteria met → should pass

---

## Expected Output Format

**Phase 3 Output (when gate passes):**
```
======================================================================
THRESHOLD_ONSET — Phase 3 (Multi-Run)
======================================================================

Node count:                <number>
Edge count:                 <number>
Total relations:            <number>
Persistent relations:       <number>
Persistence rate:          <float>
Stable relations:          <number>
Stability ratio:            <float>
Common edges ratio:         <float>
Path length count:          <number>

======================================================================
```

**CRITICAL:** Output shows **only counts**, never hash values.
- No hash values displayed
- Use numeric phrasing only (ratios, variances, counts)
- Avoid interpretive language

**Phase 3 Gate Failure:**
```
======================================================================
THRESHOLD_ONSET — Phase 3 GATE FAILED
======================================================================

Phase 3 not entered: gate criteria not met
Persistent identities:      <number>
Persistent relations:       <number>
Stability ratio:            <float>
Required stability ratio:   0.6

======================================================================
```

---

## Implementation Order

1. Implement `relation.py` - Relation hash generation
2. Implement `persistence.py` - Relation persistence measurement
3. Implement `stability.py` - Relation stability measurement
4. Update `phase3.py` - Add `phase3_multi_run()` and gate logic
5. Update `main.py` - Add `run_phase3_multi_run()` and integration
6. Test with multi-run mode
7. Verify gate logic works correctly
8. Validate freeze criteria

---

## Reference Documents

- `docs/phase3/PHASE3_PERSISTENCE.md` - Full persistence specification
- `docs/phase3/PHASE3_IMPLEMENTATION_PROMPT_FINAL.md` - Original Phase 3 prompt
- `src/phase2/phase2.py` - Reference for `phase2_multi_run()` pattern

---

## Status

**Phase 3 Completion Prompt: ✅ READY**

Proceed with implementation when ready.
