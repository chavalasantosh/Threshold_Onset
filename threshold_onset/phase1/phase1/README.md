# Phase 1 Documentation (`docs/phase1/`)

This directory contains all documentation for Phase 1 — SEGMENTATION.

## Status

**Phase 1:** 📋 **DESIGNED (not implemented)**

Phase 1 is designed but not yet implemented. Documentation exists to guide implementation.

## Contents

### `PHASE1_TRANSITION.md`
Complete transition rules from Phase 0 to Phase 1:
- Phase 1 definition
- What Phase 1 allows
- What Phase 1 forbids
- Transition criteria
- Minimal tests for segmentation emergence
- Phase 1 output specification
- Implementation constraints

### `PHASE1_IMPLEMENTATION_PROMPT_FINAL.md`
**USE THIS ONE** - Corrected and tightened implementation prompt:
- All 4 corrections applied
- Fixed threshold constraints
- Exact equality constraints
- No real-time logs
- Ready for implementation

### `PHASE1_IMPLEMENTATION_PROMPT.md`
Original implementation prompt (kept for reference):
- Contains original version before corrections
- Do not use for implementation
- Reference only

## Phase 1 Definition

**Segmentation WITHOUT naming**

Core Question: When does raw, opaque residue become separable into distinguishable parts?

## What Phase 1 Allows

✅ Boundary detection (indices only)  
✅ Clustering (counts only)  
✅ Distance measurement (raw numbers)  
✅ Pattern detection (counts only)  
✅ Structural metrics (numbers/indices only)

## What Phase 1 Forbids

❌ Names, labels, symbols  
❌ Interpretation, meaning  
❌ Classification, categorization  
❌ Visualization, plots  
❌ Adaptive thresholds  
❌ Real-time logs

## Implementation

When ready to implement Phase 1:
1. Use `PHASE1_IMPLEMENTATION_PROMPT_FINAL.md` as the prompt
2. Follow `PHASE1_TRANSITION.md` for rules
3. Ensure Phase 0 remains frozen
4. Implement in `src/phase1/`

## Related Documentation

- Phase 0: `src/phase0/docs/`
- Axioms: `docs/axioms/`
- Architecture: `docs/architecture/`
