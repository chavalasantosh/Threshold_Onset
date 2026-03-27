# Phase 2 Documentation (`docs/phase2/`)

This directory contains all documentation for Phase 2 — IDENTITY.

## Status

**Phase 2:** 📋 **DESIGNED (not implemented)**

Phase 2 is designed but not yet implemented. Documentation exists to guide implementation.

## Contents

### `PHASE2_IMPLEMENTATION_PROMPT_FINAL.md`
**USE THIS ONE** - Final implementation prompt for Phase 2:
- Complete Phase 2 definition
- What Phase 2 allows
- What Phase 2 forbids
- Implementation constraints
- Structure requirements
- Minimal tests
- Ready for implementation

## Phase 2 Definition

**Identity WITHOUT naming**

Core Question: When does a segment persist enough to deserve an identity?

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
❌ Classification with names  
❌ Using identity hashes as names or symbols  
❌ Visualization, plots, coordinates  
❌ Adaptive thresholds, learning, optimization  
❌ Real-time logs, stepwise narration

## Key Constraint

**Identity hashes are INTERNAL ONLY.**

- Hashes are for internal tracking only
- Hashes are NOT names, labels, or symbols
- Hashes are NOT to be displayed as names
- Hashes are mechanical identifiers, not meaningful labels

## Implementation

When ready to implement Phase 2:
1. Use `PHASE2_IMPLEMENTATION_PROMPT_FINAL.md` as the prompt
2. Ensure Phase 0 and Phase 1 remain frozen
3. Implement in `src/phase2/`
4. Identity hashes must be internal only

## Related Documentation

- Phase 0: `src/phase0/docs/`
- Phase 1: `src/phase1/docs/`
- Axioms: `docs/axioms/`
- Architecture: `docs/architecture/`
