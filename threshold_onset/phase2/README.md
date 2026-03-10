# Phase 2 — IDENTITY

**Status:** ✅ **IMPLEMENTED AND VERIFIED**

Phase 2 performs **identity detection without naming**.

## Core Question

**When does a segment persist enough to deserve an identity?**

Phase 2 answers: **Identity WITHOUT naming**

Identity is earned, not assigned.

## What Phase 2 Does

Phase 2 operates on opaque residues from Phase 0 and structural metrics from Phase 1, and performs:
1. **Persistence Measurement** - Tracks how long segments persist (counts only)
2. **Repeatable Unit Detection** - Identifies units that repeat (counts only)
3. **Identity Hash Generation** - Creates internal identity hashes (internal only, not symbolic)
4. **Stability Measurement** - Measures cluster stability (counts only)

**Returns identity metrics only. No naming, no interpretation.**

## Files

### Core Implementation
- `phase2.py` - Main Phase 2 pipeline
  - Function: `phase2(residues, phase1_metrics)` - returns identity metrics dictionary

### Components
- `persistence.py` - Persistence measurement (counts only)
  - Function: `measure_persistence(residue_sequences)` - returns persistence counts and hashes
  - Fixed threshold: `PERSISTENCE_THRESHOLD = 2`
  - Fixed window: `SEGMENT_WINDOW = 2`

- `repeatable.py` - Repeatable unit detection (counts only)
  - Function: `detect_repeatable_units(residues)` - returns repeatability counts and hashes
  - Fixed threshold: `REPEATABILITY_THRESHOLD = 2`
  - Fixed window: `UNIT_WINDOW = 2`

- `identity.py` - Identity hash generation (hashes only, internal)
  - Function: `assign_identity_hashes(residue_sequences)` - returns identity mappings
  - Fixed threshold: `IDENTITY_PERSISTENCE_THRESHOLD = 2`
  - Hash generation: SHA256 (internal identifier only)

- `stability.py` - Stability metrics (counts only)
  - Function: `measure_stability(cluster_sequences)` - returns stability counts and hashes
  - Fixed threshold: `STABILITY_THRESHOLD = 2`
  - Comparison: Exact equality (sorted clusters)

## Usage

```python
from phase2.phase2 import phase2

# Get residues from Phase 0 and metrics from Phase 1
residues = [0.642, 0.836, ...]  # From Phase 0
phase1_metrics = {...}  # From Phase 1

# Run Phase 2 identity detection
identity_metrics = phase2(residues, phase1_metrics)

# Metrics contain:
# - 'persistence_counts': {hash: count}  # Hash is internal only
# - 'persistent_segment_hashes': [hash, ...]  # Hashes not displayed as names
# - 'repeatability_counts': {hash: count}
# - 'repeatable_unit_hashes': [hash, ...]
# - 'identity_mappings': {segment_hash: identity_hash}
# - 'identity_persistence': {identity_hash: count}
# - 'stability_counts': {hash: count}
# - 'stable_cluster_hashes': [hash, ...]
```

## What Phase 2 Allows

✅ Persistence measurement (counts only)  
✅ Repeatable unit detection (counts only)  
✅ Identity hash generation (internal only, not symbolic)  
✅ Stability metrics (counts only)  
✅ Identity assignment (hash-based, internal only)  
✅ Fixed thresholds (external, non-adaptive)  
✅ Exact equality comparisons

## What Phase 2 Forbids

❌ Symbolic naming (names, labels, symbols)  
❌ Linguistic labels (words, tokens, letters)  
❌ Meaning, interpretation, semantic analysis  
❌ Classification, categorization with names  
❌ **Using identity hashes as names or symbols**  
❌ Visualization, plots, coordinates  
❌ Adaptive thresholds, learning, optimization  
❌ Real-time logs, stepwise narration  
❌ Pattern abstraction, compression  
❌ **Displaying hashes as meaningful labels**

## Critical Constraint

**Identity hashes are INTERNAL ONLY.**

- Hashes are for internal tracking only
- Hashes are NOT names, labels, or symbols
- Hashes are NOT to be displayed as names
- Hashes are mechanical identifiers, not meaningful labels
- Output shows only counts/lengths, not hash values

**This is the most important constraint for Phase 2.**

## Constraints

### Fixed Thresholds Only
- All thresholds are **FIXED, EXTERNAL, and NON-ADAPTIVE**
- No learning, tuning, or optimization
- Thresholds defined as constants

### Exact Comparisons Only
- All comparisons use **EXACT EQUALITY** only
- No approximate matching
- No abstraction or compression

### Phase 0 and Phase 1 Protection
- Phase 0 and Phase 1 code cannot be modified
- Phase 2 reads their output only
- No backward contamination
- Cluster reconstruction uses Phase 1 functions (reading, not modifying)

## Output Contract

**Receives:**
- Opaque residue list (floats from Phase 0)
- Phase 1 structural metrics (dictionary)

**Returns:** Dictionary with identity metrics:
- `persistence_counts`: Dict mapping segment hash to count (int)
- `persistent_segment_hashes`: List of hash values (internal only)
- `repeatability_counts`: Dict mapping unit hash to count (int)
- `repeatable_unit_hashes`: List of hash values (internal only)
- `identity_mappings`: Dict mapping segment hash to identity hash
- `identity_persistence`: Dict mapping identity hash to count (int)
- `stability_counts`: Dict mapping cluster hash to count (int)
- `stable_cluster_hashes`: List of hash values (internal only)

**No names, no labels, no interpretation. Hashes are internal only.**

## Documentation

See `docs/` subdirectory for:
- Phase 2 compliance verification
- Implementation details
- Transition rules from Phase 1

## Status

**Phase 2 is IMPLEMENTED and VERIFIED.**

- ✅ Implemented
- ✅ Verified
- ✅ Compliant
- ✅ Phase 0 and Phase 1 protected
- ✅ Ready to freeze

Phase 2 serves as the foundation for Phase 3. It must remain unchanged once frozen.
