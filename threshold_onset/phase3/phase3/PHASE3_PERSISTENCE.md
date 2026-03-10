# Phase 3 Persistence Specification

**Date:** 2026-01-13  
**Status:** 📋 **SPECIFICATION (NOT IMPLEMENTED)**

---

## Goal

**Finish Phase 3 properly.**

Phase 3 must **earn the right to be frozen**, the same way Phase 0 did.

---

## Current State (FACT)

✅ Phase 3 **executes**  
✅ Phase 3 **produces metrics**  
❌ Phase 3 **does NOT test persistence**  
❌ Phase 3 **does NOT have freeze criteria**  
❌ Phase 3 **does NOT have a gate**

**Conclusion:** Phase 3 is **exploratory**, not canonical.

---

## What "Phase 3 Complete" Must Mean

Phase 3 is complete **only if**:

1. Relations **persist across independent runs**
2. Relations **stabilize**
3. The relation graph **converges**
4. A **gate** blocks Phase 3 when this is not true

Until then, Phase 3 must remain **unfrozen**.

---

## Step 1: Define Relation Signature (STRUCTURALLY)

### Relation Hash Definition

A **relation** is a structural connection between two identities, identified by a hash.

**Relation Signature:**
```
relation_hash = hash(source_identity_hash, target_identity_hash, relation_type_hash)
```

**Components:**
- `source_identity_hash`: Identity hash of source (from Phase 2)
- `target_identity_hash`: Identity hash of target (from Phase 2)
- `relation_type_hash`: Hash identifying relation type (interaction, dependency, influence)

**Rules:**
- No names
- No semantics
- Hash-only identifiers
- Directional (source → target)
- Uses exact equality for comparison

**Relation Types (Hash-Based):**
- `INTERACTION_TYPE_HASH`: Hash for interaction relations
- `DEPENDENCY_TYPE_HASH`: Hash for dependency relations
- `INFLUENCE_TYPE_HASH`: Hash for influence relations

**CRITICAL:** Relation type hashes must be **fixed and global**, not derived dynamically.
- Use: `hashlib.sha256(b"interaction").hexdigest()` (fixed constant)
- Use: `hashlib.sha256(b"dependency").hexdigest()` (fixed constant)
- Use: `hashlib.sha256(b"influence").hexdigest()` (fixed constant)
- This avoids "relation drift" and ensures consistency across runs.

**Output:**
- `relation_hashes`: Set of relation hashes (internal identifiers only)
- `relation_counts`: Dict mapping relation_hash to occurrence count (int)

---

## Step 2: Multi-Run Relation Collection

### Multi-Run Phase 3 Function

**Function:** `phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)`

**Purpose:** Collect relations across multiple independent Phase 0 runs.

**Flow:**
1. Run Phase 0 → Phase 1 → Phase 2 **N times** (already done in main.py)
2. For each run:
   - Extract relations from Phase 3
   - Generate relation_hashes
   - Store per-run relation sets
3. Aggregate relation_hashes across all runs

**Input:**
- `residue_sequences`: List of residue sequences (one per run)
- `phase1_metrics_list`: List of Phase 1 metrics (one per run)
- `phase2_metrics`: Phase 2 metrics from multi-run (aggregated)

**Output:**
- `relation_hashes_per_run`: List of sets (one set per run)
- `relation_counts_per_run`: List of dicts (one dict per run)
- `aggregated_relation_hashes`: Set of all unique relation hashes
- `aggregated_relation_counts`: Dict mapping relation_hash to total count

**No comparison yet. Just collection.**

---

## Step 3: Relation Persistence Test

### Persistence Definition

A relation is **persistent** if:

- It appears in ≥ K runs (K ≥ 2 minimum)

**Fixed Threshold:**
- `RELATION_PERSISTENCE_THRESHOLD = 2` (minimum number of runs)

**Metrics:**
- `total_relations`: Total number of unique relations across all runs (int)
- `persistent_relations`: Number of relations appearing in ≥ K runs (int)
- `persistence_rate`: `persistent_relations / total_relations` (float, 0.0 to 1.0)
- `persistent_relation_hashes`: Set of relation hashes that are persistent

**Implementation:**
- For each relation_hash in aggregated_relation_hashes:
  - Count how many runs contain this relation_hash
  - If count ≥ RELATION_PERSISTENCE_THRESHOLD:
    - Mark as persistent
    - Add to persistent_relation_hashes

**Output:**
- `persistence_counts`: Dict mapping relation_hash to persistence count (int)
- `persistent_relation_hashes`: Set of persistent relation hashes
- `persistence_rate`: Float (0.0 to 1.0)

**No graph analysis yet. Just persistence counts.**

---

## Step 4: Relation Stability Metric

### Stability Definition (NUMERICAL ONLY)

Stability measures **numerical consistency** of relations across runs.

**Stability Metrics:**

**CRITICAL:** Stability is **secondary to persistence**, not parallel.
- First: Filter to persistent relations only
- Then: Measure stability **only on persistent relations**
- Do **NOT** compute stability on transient relations

1. **Frequency Stability:**
   - For each **persistent** relation_hash (already filtered):
     - Count occurrences in each run
     - Compute variance of occurrence counts
     - Low variance = high stability

2. **Edge Density Stability:**
   - Compute edge_count / node_count for each run
   - Compute variance of edge density
   - Low variance = high stability

3. **Graph Structure Stability:**
   - Compare graph_edges sets across runs
   - Count common edges (intersection)
   - Common edges / total edges = stability ratio

**Fixed Thresholds:**
- `STABILITY_VARIANCE_THRESHOLD = 2.0` (maximum variance for stable relations)
- `STABILITY_RATIO_THRESHOLD = 0.6` (minimum ratio for stable graph)

**Output:**
- `stability_counts`: Dict mapping relation_hash to stability count (int)
- `stable_relation_hashes`: Set of stable relation hashes
- `stability_ratio`: Float (0.0 to 1.0) - ratio of stable relations
- `edge_density_variance`: Float - variance of edge density across runs
- `common_edges_ratio`: Float (0.0 to 1.0) - ratio of common edges across runs

**Still no meaning. Just numbers.**

---

## Step 5: Phase 3 Gate (CRITICAL)

### Gate Requirements

Phase 3 **must refuse to finalize** unless:

1. Phase 2 produced persistent identities:
   - `len(phase2_metrics['persistent_segment_hashes']) > 0` OR
   - `len(phase2_metrics['identity_mappings']) > 0`

2. Persistent relations exist:
   - `persistent_relations > 0`

3. Stability threshold met:
   - `stability_ratio >= STABILITY_RATIO_THRESHOLD` (0.6)

**Gate Logic:**
```python
if not (has_persistent_identities and persistent_relations > 0 and stability_ratio >= STABILITY_RATIO_THRESHOLD):
    return None  # Refuse execution
```

**If gate fails:**
- Phase 3 returns `None`
- Phase 4 is blocked automatically
- Output shows gate failure message

**Gate Output:**
- Shows which criteria failed
- Shows actual values vs thresholds
- No execution if gate fails

---

## Step 6: Phase 3 Freeze Criteria

### Freeze Requirements

Phase 3 can be frozen **only when**:

1. ✅ Persistent relations exist: `persistent_relations > 0`
2. ✅ Stability confirmed: `stability_count > 0`
3. ✅ Graph structure converges: `common_edges_ratio >= 0.6`
4. ✅ Repeated executions produce similar metrics:
   - Edge count variance < threshold
   - Node count variance < threshold
   - Relation count variance < threshold

**Freeze Validation:**
- Run Phase 3 multiple times (same configuration)
- Compare metrics across runs
- If metrics are consistent → ready to freeze
- If metrics vary significantly → not ready

**Once Frozen:**
- Phase 3 code becomes read-only
- Outputs become canonical
- No further modifications allowed
- Serves as foundation for Phase 4

---

## Implementation Structure

### New Files Required

1. **`src/phase3/relation.py`**
   - `generate_relation_hash(source_hash, target_hash, relation_type_hash)`
   - `extract_relations(phase3_metrics)` → returns relation_hashes

2. **`src/phase3/persistence.py`**
   - `measure_relation_persistence(relation_hashes_per_run, threshold=RELATION_PERSISTENCE_THRESHOLD)`
   - Returns persistence metrics

3. **`src/phase3/stability.py`**
   - `measure_relation_stability(relation_hashes_per_run, relation_counts_per_run)`
   - Returns stability metrics

4. **`src/phase3/phase3.py`** (UPDATE)
   - Add `phase3_multi_run()` function
   - Add gate logic
   - Add persistence and stability computation

### Updated Files

1. **`main.py`**
   - Update `run_phase3()` to support multi-run
   - Add `run_phase3_multi_run()` function
   - Integrate gate checks

---

## Fixed Thresholds (ALL EXTERNAL, NON-ADAPTIVE)

```python
# Relation persistence
RELATION_PERSISTENCE_THRESHOLD = 2  # Minimum runs for persistence

# Stability
STABILITY_VARIANCE_THRESHOLD = 2.0  # Maximum variance for stable relations
STABILITY_RATIO_THRESHOLD = 0.6     # Minimum ratio for stable graph

# Gate thresholds
MIN_PERSISTENT_RELATIONS = 1        # Minimum persistent relations required
MIN_STABILITY_RATIO = 0.6           # Minimum stability ratio required
```

**All thresholds are FIXED constants. No adaptation, no learning, no optimization.**

---

## Output Contract (Multi-Run Phase 3)

**Receives:**
- `residue_sequences`: List of residue sequences (one per run)
- `phase1_metrics_list`: List of Phase 1 metrics (one per run)
- `phase2_metrics`: Phase 2 metrics from multi-run (aggregated)

**Returns:** Dictionary with relation metrics:
- `relation_hashes`: Set of all relation hashes (internal identifiers only)
- `relation_counts`: Dict mapping relation_hash to total count (int)
- `persistent_relation_hashes`: Set of persistent relation hashes
- `persistence_rate`: Float (0.0 to 1.0)
- `stable_relation_hashes`: Set of stable relation hashes
- `stability_ratio`: Float (0.0 to 1.0)
- `edge_density_variance`: Float
- `common_edges_ratio`: Float (0.0 to 1.0)
- `graph_nodes`: Set of identity hashes (from aggregated graph)
- `graph_edges`: Set of edge tuples (from aggregated graph)
- `node_count`: Number of nodes (int)
- `edge_count`: Number of edges (int)

**All hashes are internal identifiers only. No names, no labels, no visualization.**

**CRITICAL OUTPUT CONSTRAINTS:**
- `main.py` prints **only counts**, never hash values
- Use numeric phrasing only (e.g., `common_edges_ratio`, `edge_density_variance`)
- Avoid interpretive language (e.g., "graph converges" → use `common_edges_ratio >= 0.6`)
- All outputs are numbers/lengths, no hash values displayed

---

## What Must NOT Be Done

❌ Do NOT touch Phase 4  
❌ Do NOT introduce symbols  
❌ Do NOT visualize graphs  
❌ Do NOT explain relations semantically  
❌ Do NOT relax gates "just to see"  
❌ Do NOT use adaptive thresholds  
❌ Do NOT add meaning or interpretation  

---

## What Comes After (NOT NOW)

Only after Phase 3 is frozen:

- Phase 4: SYMBOL
- Letters, tokens, names
- Symbolic representation
- Alphabet ideas belong **there**, not before

---

## Implementation Order

1. ✅ Define relation_hash formally (this document)
2. ⏳ Implement `relation.py` - Relation hash generation
3. ⏳ Implement `persistence.py` - Relation persistence measurement
4. ⏳ Implement `stability.py` - Relation stability measurement
5. ⏳ Update `phase3.py` - Add `phase3_multi_run()` function
6. ⏳ Update `main.py` - Add `run_phase3_multi_run()` function
7. ⏳ Add gate logic to Phase 3
8. ⏳ Test multi-run persistence
9. ⏳ Validate freeze criteria
10. ⏳ Freeze Phase 3 (when criteria met)

---

## Status

**Phase 3 Persistence Specification: ✅ COMPLETE**

Ready for implementation.
