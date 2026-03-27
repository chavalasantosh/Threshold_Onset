# Phase 3 Completion — Final Implementation Prompt

**Date:** 2026-01-13  
**Status:** ✅ **APPROVED — DO NOT DEVIATE**

---

## Verdict

**This plan is fundamentally correct and safe to proceed with.**

- ✅ Architecturally sound
- ✅ Consistent with phase doctrine
- ✅ Correctly delayed (does not jump to symbols)
- ✅ Properly multi-run–aware
- ✅ Gate-driven (critical part)

**This is exactly how Phase 3 should be finished.**

---

## Critical Constraints (NON-NEGOTIABLE)

### 1. Relation Type Hashes Must Be Fixed and Global

**DO:**
```python
# At module level (computed once)
INTERACTION_TYPE_HASH = hashlib.sha256(b"interaction").hexdigest()
DEPENDENCY_TYPE_HASH = hashlib.sha256(b"dependency").hexdigest()
INFLUENCE_TYPE_HASH = hashlib.sha256(b"influence").hexdigest()
```

**DON'T:**
- Compute relation type hashes dynamically per-call
- Derive hashes from variable inputs
- Allow "relation drift"

**Why:** Ensures consistency across runs and avoids relation drift.

---

### 2. Stability Is Secondary to Persistence

**DO:**
1. First: Filter to persistent relations only
2. Then: Measure stability **only on persistent relations**

**DON'T:**
- Compute stability on transient relations
- Measure stability in parallel with persistence
- Include non-persistent relations in stability calculations

**Why:** Stability is a property of persistent relations, not all relations.

---

### 3. Output Shows Only Counts, Never Hash Values

**DO:**
- Print counts: `len(relation_hashes)`, `len(persistent_relation_hashes)`
- Print ratios: `persistence_rate`, `stability_ratio`, `common_edges_ratio`
- Print variances: `edge_density_variance`

**DON'T:**
- Display hash values: `print(relation_hash)` ❌
- Show hash strings in output ❌
- Use hash values as labels or names ❌

**Why:** Keeps Phase 3 non-symbolic. Hashes are internal identifiers only.

---

### 4. Use Numeric Phrasing Only

**DO:**
- `common_edges_ratio >= 0.6`
- `edge_density_variance < 2.0`
- `persistence_rate = 0.75`

**DON'T:**
- "Graph converges" (interpretive language) ❌
- "Relations stabilize" (interpretive language) ❌
- "Structure emerges" (interpretive language) ❌

**Why:** Avoids interpretive language. Use numbers only.

---

## Implementation Order (STRICT)

**Proceed exactly in this order:**

1. ✅ Implement `relation.py` - Relation hash generation
2. ✅ Implement `persistence.py` - Relation persistence measurement
3. ✅ Implement `stability.py` - Relation stability measurement (ONLY on persistent relations)
4. ✅ Update `phase3.py` - Add `phase3_multi_run()` function
5. ✅ Add gate logic to `phase3.py`
6. ✅ Update `main.py` - Add `run_phase3_multi_run()` function
7. ✅ Test multi-run convergence
8. ✅ Freeze Phase 3 **only if metrics stabilize**

**Then and only then** touch Phase 4.

---

## File Structure

### New Files

1. **`src/phase3/relation.py`**
   - `generate_relation_hash(source_hash, target_hash, relation_type_hash)`
   - `extract_relations(phase3_metrics)`
   - Fixed relation type hashes at module level

2. **`src/phase3/persistence.py`**
   - `measure_relation_persistence(relation_hashes_per_run, threshold=RELATION_PERSISTENCE_THRESHOLD)`
   - Returns: persistence_counts, persistent_relation_hashes, persistence_rate

3. **`src/phase3/stability.py`**
   - `measure_relation_stability(relation_hashes_per_run, relation_counts_per_run, graph_metrics_per_run, persistent_relation_hashes)`
   - **CRITICAL:** Only measures stability on persistent_relation_hashes
   - Returns: stability_counts, stable_relation_hashes, stability_ratio, edge_density_variance, common_edges_ratio

### Updated Files

1. **`src/phase3/phase3.py`**
   - Add `phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)`
   - Add `_check_phase3_gate(phase2_metrics, persistent_relations, stability_ratio)`
   - Orchestrate: collection → persistence → stability → gate

2. **`main.py`**
   - Add `run_phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)`
   - Update multi-run mode to call `run_phase3_multi_run()`
   - **CRITICAL:** Output shows only counts, never hash values

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

## Gate Logic (CRITICAL)

**Phase 3 must refuse execution unless ALL three criteria are met:**

1. Phase 2 produced persistent identities:
   - `len(phase2_metrics.get('persistent_segment_hashes', [])) > 0` OR
   - `len(phase2_metrics.get('identity_mappings', {})) > 0`

2. Persistent relations exist:
   - `persistent_relations >= MIN_PERSISTENT_RELATIONS` (≥ 1)

3. Stability threshold met:
   - `stability_ratio >= MIN_STABILITY_RATIO` (≥ 0.6)

**If gate fails:**
- Return `None` from `phase3_multi_run()`
- Print gate failure message with actual values vs thresholds
- Do not compute or return relation metrics

---

## Output Format

### Gate Passes

```
======================================================================
THRESHOLD_ONSET — Phase 3 (Multi-Run)
======================================================================

Node count:                <number>
Edge count:                 <number>
Total relations:            <number>
Persistent relations:       <number>
Persistence rate:          <float>
Stable relations:           <number>
Stability ratio:            <float>
Common edges ratio:         <float>
Path length count:          <number>

======================================================================
```

### Gate Fails

```
======================================================================
THRESHOLD_ONSET — Phase 3 GATE FAILED
======================================================================

Phase 3 not entered: gate criteria not met
Persistent identities:      <number>
Persistent relations:        <number>
Stability ratio:             <float>
Required stability ratio:    0.6

======================================================================
```

**CRITICAL:** All outputs are numbers/lengths. No hash values displayed.

---

## What Must NOT Be Done

❌ Do NOT modify Phase 0, Phase 1, or Phase 2 code  
❌ Do NOT introduce symbols, names, or labels  
❌ Do NOT visualize graphs (plots, coordinates, visual graphs)  
❌ Do NOT explain relations semantically  
❌ Do NOT relax gates "just to see"  
❌ Do NOT use adaptive thresholds, learning, or optimization  
❌ Do NOT display hash values in output  
❌ Do NOT use interpretive language  
❌ Do NOT compute stability on transient relations  
❌ Do NOT derive relation type hashes dynamically  

---

## What Must Be Done

✅ Use fixed thresholds only (defined as constants)  
✅ Use exact equality for hash comparison  
✅ Return only numbers/hash pairs (no names, no labels)  
✅ Graph structures are internal only (not displayed)  
✅ All hashes are internal identifiers only  
✅ Output shows only counts/lengths (no hash values displayed)  
✅ Measure stability ONLY on persistent relations  
✅ Use numeric phrasing only (ratios, variances, counts)  
✅ Relation type hashes are fixed and global  

---

## Testing Checklist

Before considering Phase 3 complete:

- [ ] Relation hashes are generated correctly (same inputs → same hash)
- [ ] Persistence is measured across multiple runs (≥ 2 runs)
- [ ] Stability is measured ONLY on persistent relations
- [ ] Gate blocks execution when criteria not met
- [ ] Gate allows execution when all criteria met
- [ ] Output shows only counts, never hash values
- [ ] Multi-run produces consistent metrics
- [ ] Relation type hashes are fixed and global
- [ ] No modification to Phase 0, Phase 1, or Phase 2

---

## Final Truth

**This is not a toy system anymore — this is real groundwork.**

Phase 3 must **earn the right to be frozen**, the same way Phase 0 did.

Proceed with discipline. Do not deviate.

---

## Status

**Phase 3 Final Implementation Prompt: ✅ APPROVED**

**Ready for implementation. Do not deviate from this specification.**
