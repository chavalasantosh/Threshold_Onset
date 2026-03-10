# Phase 0 → Phase 1 Transition Rules

## Status

**Phase 0:** ✅ FROZEN (permanent, unmodifiable)  
**Phase 1:** 📋 DESIGNED (not implemented)  
**Transition:** 🔄 RULES DEFINED

---

## Phase 1 Definition

### Core Question

**When does raw, opaque residue become separable into distinguishable parts?**

Phase 1 answers: **Segmentation without naming**

---

## What Phase 1 Allows (New Capabilities)

### 1. Boundary Detection
- Detect where one residue differs from another
- Identify separation points
- Find discontinuities
- **NOT allowed:** Name the boundaries, label them, interpret them

### 2. Difference Measurement
- Compute distance between residues
- Measure similarity/dissimilarity
- Quantify separation
- **NOT allowed:** Classify differences, name types of differences

### 3. Clustering
- Group residues by proximity
- Identify clusters
- Count cluster sizes
- **NOT allowed:** Name clusters, label groups, interpret clusters

### 4. Pattern Detection
- Detect repetition in residue sequences
- Identify recurring structures
- Find invariants under transformation
- **NOT allowed:** Name patterns, interpret meaning, assign symbols

### 5. Structural Metrics
- Cluster count
- Cluster size distribution (counts only)
- Separation distances (raw numbers)
- Boundary positions (indices only)
- **NOT allowed:** Min/max interpretation, statistical analysis beyond counts

---

## What Phase 1 Forbids (Still Not Allowed)

### Remains Forbidden:
- ❌ Symbols
- ❌ Labels
- ❌ Names
- ❌ IDs
- ❌ Meaning
- ❌ Interpretation
- ❌ Semantic analysis
- ❌ Classification
- ❌ Categorization
- ❌ Tokenization
- ❌ Embeddings
- ❌ Visualization (plots, coordinates)
- ❌ Statistical analysis (beyond counts)
- ❌ Min/max interpretation
- ❌ Range interpretation
- ❌ Distribution interpretation

---

## Transition Criteria (Phase 0 → Phase 1)

### When Phase 1 Can Begin

Phase 1 begins when **ALL** of these conditions are met:

1. **Repetition Pressure Exists**
   - Phase 0 has run for sufficient iterations
   - Residues have been collected under repetition
   - No premature transition

2. **Collision Rate Threshold**
   - Collision rate > 0 (some residues repeat)
   - OR collision rate = 0 but sufficient sample size
   - Threshold: TBD (empirical)

3. **Segmentation Signal Detected**
   - Can detect boundaries between residue groups
   - Can measure differences between residues
   - Can identify clusters without naming them

4. **Phase 0 Output Stable**
   - Residue collection is consistent
   - No interpretation has been applied
   - Phase 0 constraints still enforced

---

## Minimal Tests for Segmentation Emergence

### Test 1: Boundary Detection
**Question:** Can we detect where residue sequences change?

**Method:**
- Compare consecutive residues
- Compute difference metric (raw number)
- Identify positions where difference exceeds threshold
- Return: boundary positions (indices only)

**Pass Criteria:**
- Boundaries detected
- No labels assigned
- Only indices returned

### Test 2: Clustering
**Question:** Can residues be grouped by proximity?

**Method:**
- Compute pairwise distances (raw numbers)
- Group residues within distance threshold
- Count groups
- Return: group counts, group sizes (numbers only)

**Pass Criteria:**
- Groups identified
- No group names
- Only counts returned

### Test 3: Pattern Repetition
**Question:** Do residue sequences repeat?

**Method:**
- Compare residue subsequences
- Detect exact matches (raw comparison)
- Count repetition frequency
- Return: repetition count (number only)

**Pass Criteria:**
- Repetitions detected
- No pattern names
- Only counts returned

### Test 4: Structural Invariance
**Question:** Do certain structures persist under repetition?

**Method:**
- Track residue sequences across iterations
- Identify sequences that survive
- Count survival frequency
- Return: survival counts (numbers only)

**Pass Criteria:**
- Invariants identified
- No structure names
- Only counts returned

---

## Phase 1 Output Specification

### Allowed Output:
- Boundary positions (indices)
- Cluster counts
- Cluster sizes (counts)
- Distance measurements (raw numbers)
- Repetition counts
- Survival counts
- Separation metrics (raw numbers)

### Forbidden Output:
- Cluster names
- Boundary labels
- Pattern names
- Structure names
- Interpretations
- Classifications
- Meanings

---

## Implementation Constraints

### Phase 1 Code Must:
- Accept Phase 0 residues as input
- Not modify Phase 0 code
- Operate on opaque residues
- Return only structural metrics (no names)
- Enforce segmentation without naming

### Phase 1 Code Must NOT:
- Add labels to residues
- Name clusters or groups
- Interpret boundaries
- Create symbols
- Assign meaning
- Modify Phase 0

---

## Transition Implementation Rules

### Rule 1: Phase 0 Remains Frozen
- Phase 0 code cannot be modified
- Phase 0 output format cannot change
- Phase 1 reads Phase 0 output only

### Rule 2: No Backward Contamination
- Phase 1 cannot add features to Phase 0
- Phase 1 operates as separate layer
- Phase 0 constraints remain enforced

### Rule 3: Minimal Interface
- Phase 1 receives: residue list (opaque)
- Phase 1 returns: structural metrics (numbers only)
- No shared state with Phase 0

### Rule 4: Test-Driven Transition
- Phase 1 begins only when tests pass
- Tests must be minimal and verifiable
- No transition without test validation

---

## Phase 1 Structure (Proposed)

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

---

## Validation Checklist

Before Phase 1 implementation:

- [ ] Phase 0 is frozen and unmodified
- [ ] Transition criteria are met
- [ ] Minimal tests are defined
- [ ] Phase 1 boundaries are clear
- [ ] No naming/interpretation allowed
- [ ] Output specification is precise
- [ ] Implementation constraints are defined

---

**Status:** Transition rules defined. Phase 1 ready for design when criteria are met.
