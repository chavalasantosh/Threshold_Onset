# Phase 3 Documentation (`src/phase3/phase3/`)

This directory contains design documentation for Phase 3 — RELATION.

## Status

**Phase 3:** 🔒 **FROZEN FOREVER** (as of 2026-01-14)

Phase 3 is implemented, validated, and frozen. See `docs/phase3/PHASE3_FREEZE.md` for freeze declaration.

## Contents

### `PHASE3_IMPLEMENTATION_PROMPT_FINAL.md`
**USE THIS ONE** - Final implementation prompt for Phase 3:
- Complete Phase 3 definition
- What Phase 3 allows
- What Phase 3 forbids
- Implementation constraints
- Structure requirements
- Minimal tests
- Ready for implementation

## Phase 3 Definition

**Relation WITHOUT naming**

Core Question: How do identities influence one another?

## What Phase 3 Allows

✅ Graph structure construction (hash pairs only)  
✅ Interaction detection (counts and hash pairs)  
✅ Dependency measurement (counts and hash pairs)  
✅ Influence metrics (numbers only)  
✅ Graph metrics (node count, edge count, degree counts, path lengths)  
✅ Fixed thresholds (external, non-adaptive)  
✅ Exact equality comparisons

## What Phase 3 Forbids

❌ Symbolic naming (names, labels, symbols)  
❌ Linguistic labels (words, tokens, letters)  
❌ Meaning, interpretation, semantic analysis  
❌ Classification with names  
❌ Using identity hashes as names or symbols  
❌ **Graph visualization (plots, coordinates, visual graphs)**  
❌ Node labels, edge labels, path names  
❌ Adaptive thresholds, learning, optimization  
❌ Real-time logs, stepwise narration

## Key Constraints

**Graph structures are INTERNAL ONLY.**

- Graphs use identity hashes as node identifiers (internal only)
- Edges are hash pairs (internal identifiers only)
- Graphs are NOT to be displayed with names or labels
- Graphs are structural representations, not symbolic networks
- No graph visualization (plots, coordinates, visual graphs)

**This is the most important constraint for Phase 3.**

## Implementation

When ready to implement Phase 3:
1. Use `PHASE3_IMPLEMENTATION_PROMPT_FINAL.md` as the prompt
2. Ensure Phase 0, Phase 1, and Phase 2 remain frozen
3. Implement in `src/phase3/`
4. Graph structures must use hashes only (not displayed as names)

## Related Documentation

- Phase 0: `src/phase0/docs/`
- Phase 1: `src/phase1/docs/`
- Phase 2: `src/phase2/docs/`
- Axioms: `docs/axioms/`
- Architecture: `docs/architecture/`
