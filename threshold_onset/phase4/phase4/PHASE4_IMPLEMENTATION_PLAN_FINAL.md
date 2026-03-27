# Phase 4 Implementation Plan: Pure Aliasing (FINAL)

**Date:** 2026-01-14  
**Status:** ✅ **CANONICAL — NON-NEGOTIABLE**

---

## Core Principle

> **Removing all symbols must restore Phase 3 bit-for-bit, without recomputation.**

**A Phase 4 alias must be removable without recomputation.**

---

## Overview

Implement Phase 4 as a **pure aliasing layer** that creates reversible lookup tables for identity hashes and relation hashes. Phase 4 adds zero structure - it only creates aliases that can be removed without recomputation.

---

## Implementation Structure

### Files to Create

1. **`src/phase4/alias.py`** - Core aliasing logic
   - `assign_identity_aliases(identity_hashes)` → identity_hash → symbol mapping
   - `assign_relation_aliases(relation_hashes)` → relation_hash → symbol mapping
   - Deterministic symbol assignment (same input → same symbols)
   - Reversible mappings (bidirectional dictionaries)

2. **`src/phase4/phase4.py`** - Phase 4 pipeline
   - `phase4(phase2_metrics, phase3_metrics)` - Main entry point
   - Gate check (Phase 3 must be frozen)
   - Extract identity hashes from Phase 2
   - Extract relation hashes from Phase 3
   - Assign aliases
   - Return reversible mappings

3. **`src/phase4/__init__.py`** - Module initialization

### Files to Update

1. **`main.py`** - Add Phase 4 execution
   - `run_phase4_multi_run(phase2_metrics, phase3_metrics)` function
   - Add Phase 4 call after Phase 3 in multi-run mode
   - Output only counts (never symbol values)

---

## Phase 4 Inputs (From Frozen Phases)

### From Phase 2 (multi-run output):

- `persistent_segment_hashes`: list of persistent segment hashes
- `identity_mappings`: dict mapping segment_hash → identity_hash
- **Extract:** All unique identity hashes from `identity_mappings.values()`

**CRITICAL:** Phase 4 aliases apply ONLY to frozen identities and frozen relations. No alias may be created for non-persistent entities.

### From Phase 3 (multi-run output):

- `persistent_relation_hashes`: set of persistent relation hashes
- **Extract:** All persistent relation hashes

**Nothing else. No raw data. No statistics. No probabilities. Only frozen structure.**

---

## Phase 4 Outputs

### Two Reversible Maps:

1. **Identity Alias Map:**
   ```python
   {
       'identity_to_symbol': dict mapping identity_hash → symbol,
       'symbol_to_identity': dict mapping symbol → identity_hash,
       'identity_alias_count': int
   }
   ```

2. **Relation Alias Map:**
   ```python
   {
       'relation_to_symbol': dict mapping relation_hash → symbol,
       'symbol_to_relation': dict mapping symbol → relation_hash,
       'relation_alias_count': int
   }
   ```

### Combined Output:

```python
{
    'identity_to_symbol': dict,
    'symbol_to_identity': dict,
    'identity_alias_count': int,
    'relation_to_symbol': dict,
    'symbol_to_relation': dict,
    'relation_alias_count': int
}
```

**NOTE:** No `total_symbols` - identity and relation symbols are in different namespaces.

---

## Symbol Assignment Rules

### Symbol Type: INTEGERS ONLY

**CRITICAL:** Symbols are integers: `0, 1, 2, 3, ...`

**NOT letters (A, B, C)**
**NOT tokens (s0, s1, s2)**
**NOT multi-letter sequences (AA, AB, ...)**

**Why:** Integers are neutral, non-semantic, non-linguistic, safest possible alias.

### Deterministic Assignment:

- Same identity/relation hashes → same symbols
- **Aliases are assigned by iterating over sorted hashes (lexicographic)**
- This guarantees cross-machine consistency, cross-run consistency, future-proof determinism

### Alias Immutability:

- **Phase 4 must refuse to reassign symbols if a mapping already exists**
- **Existing alias tables are append-only**
- Once assigned, never changes
- Prevents silent remapping across runs

### Reversibility:

- Both directions must exist (hash → symbol, symbol → hash)
- Removing symbols = removing the mapping, not recomputing Phase 3

---

## Critical Constraints

### Must NOT:

- ❌ Add any structure beyond aliases
- ❌ Display symbol values (only counts)
- ❌ Modify Phase 0, 1, 2, or 3
- ❌ Add meaning or interpretation
- ❌ Use adaptive assignment
- ❌ Require recomputation to reverse
- ❌ **Store symbol sequences** (any sequence view must be derived on-the-fly and discarded immediately)
- ❌ Use alphabetic symbols (letters, tokens, multi-letter)
- ❌ Create aliases for non-persistent entities

### Must:

- ✅ Use integer symbols only (0, 1, 2, 3, ...)
- ✅ Use deterministic symbol assignment (sorted hashes)
- ✅ Create reversible mappings (both directions)
- ✅ Pass gate (Phase 3 frozen)
- ✅ Output only counts (no symbol values)
- ✅ Be removable without recomputation
- ✅ Enforce immutability (append-only alias tables)
- ✅ Alias only persistent identities and relations

---

## Phase 4 Gate

### Gate Criteria:

1. Phase 3 is frozen (check: `phase3_metrics is not None`)
2. Phase 3 has persistent relations (`len(persistent_relation_hashes) > 0`)
3. Phase 2 has persistent identities (`len(identity_mappings) > 0` OR `len(persistent_segment_hashes) > 0`)

### Gate Logic:

```python
def _check_phase4_gate(phase2_metrics, phase3_metrics):
    """
    Check if Phase 4 gate criteria are met.
    
    Phase 4 must refuse execution unless ALL criteria are met:
    1. Phase 3 is frozen (not None)
    2. Phase 3 has persistent relations
    3. Phase 2 has persistent identities
    
    Returns:
        True if gate passes, False if gate fails
    """
    if phase3_metrics is None:
        return False
    
    persistent_relations = len(phase3_metrics.get('persistent_relation_hashes', []))
    has_persistent_relations = persistent_relations > 0
    
    persistent_segments = len(phase2_metrics.get('persistent_segment_hashes', []))
    identity_mappings = len(phase2_metrics.get('identity_mappings', {}))
    has_persistent_identities = persistent_segments > 0 or identity_mappings > 0
    
    return has_persistent_relations and has_persistent_identities
```

**If gate fails → return None (refuse execution)**

---

## Phase 4 Freeze Criteria

Phase 4 can be frozen **only when**:

1. ✅ Alias assignment is deterministic (same input → same aliases)
2. ✅ Alias removal restores Phase 3 exactly (bit-for-bit, no recomputation)
3. ✅ Multiple runs produce identical alias tables
4. ✅ Immutability enforced (no reassignment)
5. ✅ Only persistent entities aliased

**When frozen:**
- Phase 4 becomes read-only
- Aliases become canonical
- No further modifications allowed

---

## Implementation Order

1. Create `src/phase4/alias.py` with integer symbol assignment
2. Create `src/phase4/phase4.py` with pipeline and gate
3. Create `src/phase4/__init__.py`
4. Update `main.py` with `run_phase4_multi_run()`
5. Test gate logic
6. Test reversibility (removing symbols restores Phase 3)
7. Test determinism (multiple runs produce identical tables)
8. Validate freeze criteria

---

## The One Test Phase 4 Must Always Pass

> **Delete Phase 4.
> Run Phase 3 output comparison.
> They must be identical (bit-for-bit, no recomputation).**

If not → Phase 4 failed.

---

## Final Checklist

Before implementing, verify:

- ✅ Symbols are integers only (0, 1, 2, 3, ...)
- ✅ No symbol sequences stored
- ✅ Aliases only for persistent entities
- ✅ Assignment order = sorted hashes (explicit)
- ✅ Alias tables are append-only (immutability)
- ✅ Gate checks Phase 3 frozen
- ✅ Output shows only counts (no symbol values)
- ✅ Reversible mappings (both directions)
- ✅ No `total_symbols` in output

---

**End of Plan**

*This plan is canonical and non-negotiable. All corrections from review have been incorporated.*
