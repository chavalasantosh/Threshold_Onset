# Phase 1 — SEGMENTATION

**Status:** ✅ **IMPLEMENTED AND VERIFIED**

Phase 1 performs **segmentation without naming**.

## Core Question

**When does raw, opaque residue become separable into distinguishable parts?**

Phase 1 answers: **Segmentation without naming**

## What Phase 1 Does

Phase 1 operates on opaque residues from Phase 0 and performs:
1. **Boundary Detection** - Finds separation points (indices only)
2. **Clustering** - Groups residues by proximity (counts only)
3. **Distance Measurement** - Computes pairwise distances (raw numbers)
4. **Pattern Detection** - Detects exact repetition (counts only)

**Returns structural metrics only. No naming, no interpretation.**

## Files

### Core Implementation
- `phase1.py` - Main Phase 1 pipeline
  - Function: `phase1(residues)` - returns structural metrics dictionary

### Components
- `boundary.py` - Boundary detection (indices only)
  - Function: `detect_boundaries(residues)` - returns list of boundary indices
  - Fixed threshold: `BOUNDARY_THRESHOLD = 0.1`

- `cluster.py` - Clustering (counts only)
  - Function: `cluster_residues(residues)` - returns cluster count and sizes
  - Fixed threshold: `CLUSTER_THRESHOLD = 0.1`

- `distance.py` - Distance measurement (raw numbers)
  - Function: `pairwise_distances(residues)` - returns list of distances
  - Metric: Absolute difference (mechanical)

- `pattern.py` - Pattern detection (counts only)
  - Function: `detect_repetition(residues)` - returns repetition count
  - Fixed window: `PATTERN_WINDOW_SIZE = 2`
  - Comparison: Exact equality only

## Usage

```python
from phase1.phase1 import phase1

# Get residues from Phase 0
residues = [0.642, 0.836, 0.776, ...]  # Opaque floats from Phase 0

# Run Phase 1 segmentation
metrics = phase1(residues)

# Metrics contain:
# - 'boundary_positions': [1, 2, 3, ...]  # Indices only
# - 'cluster_count': 7                    # Number only
# - 'cluster_sizes': [1, 6, 3, ...]      # Unordered list
# - 'distances': [0.194, 0.06, ...]      # Raw numbers
# - 'repetition_count': 0                # Number only
# - 'survival_count': 0                  # Number only
```

## What Phase 1 Allows

✅ Boundary detection (indices only)  
✅ Clustering (counts only)  
✅ Distance measurement (raw numbers)  
✅ Pattern detection (counts only)  
✅ Structural metrics (numbers/indices only)  
✅ Fixed thresholds (external, non-adaptive)  
✅ Exact equality comparisons

## What Phase 1 Forbids

❌ Names, labels, symbols  
❌ Meaning, interpretation  
❌ Classification, categorization  
❌ Visualization, plots, coordinates  
❌ Adaptive thresholds, learning, optimization  
❌ Real-time logs, stepwise narration  
❌ Pattern abstraction, compression  
❌ Distribution interpretation

## Constraints

### Fixed Thresholds Only
- All thresholds are **FIXED, EXTERNAL, and NON-ADAPTIVE**
- No learning, tuning, or optimization
- Thresholds defined as constants

### Exact Comparisons Only
- Pattern detection uses **EXACT EQUALITY** only
- No approximate matching
- No abstraction or compression

### Phase 0 Protection
- Phase 0 code cannot be modified
- Phase 1 reads Phase 0 output only
- No backward contamination

## Output Contract

**Receives:** Opaque residue list (floats from Phase 0)

**Returns:** Dictionary with structural metrics:
- `boundary_positions`: List of indices (int)
- `cluster_count`: Number (int)
- `cluster_sizes`: Unordered list of sizes (int)
- `distances`: List of raw numbers (float)
- `repetition_count`: Number (int)
- `survival_count`: Number (int)

**No names, no labels, no interpretation.**

## Documentation

See `docs/` subdirectory for:
- Phase 1 compliance verification
- Implementation details
- Transition rules from Phase 0

## Status

**Phase 1 is IMPLEMENTED and VERIFIED.**

- ✅ Implemented
- ✅ Verified
- ✅ Compliant
- ✅ Ready to freeze

Phase 1 serves as the foundation for Phase 2. It must remain unchanged once frozen.
