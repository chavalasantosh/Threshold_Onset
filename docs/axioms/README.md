# Axioms (`docs/axioms/`)

This directory contains the core non-negotiable design constraints for THRESHOLD_ONSET.

## Contents

### `AXIOMS.md`
Complete axiom definitions organized in layers:
- **Layer 0** - Non-negotiable core axiom (कार्य before ज्ञान)
- **Layer 1** - THRESHOLD_ONSET scope boundary
- **Layer 2** - Phase 0 outputs
- **Layer 3** - Why letters are NOT in Phase 0
- **Layer 4** - Phase 0 → Phase 1 transition rules

## Purpose

These axioms define:
1. What is allowed in each phase
2. What is forbidden in each phase
3. Phase boundaries and constraints
4. Transition rules between phases

## Core Axiom

**कार्य (kārya) happens before ज्ञान (jñāna)**

Function stabilizes before knowledge appears.

This is not philosophy. This is a design constraint.

## Usage

**All code must comply with these axioms.**

Before implementing any feature:
1. Check which phase it belongs to
2. Verify it's allowed in that phase
3. Ensure it doesn't violate phase boundaries

## Status

Axioms are:
- ✅ Defined
- ✅ Documented
- ✅ Enforced in code
- 🔒 **Non-negotiable**

## Related Documentation

- Phase 0: `src/phase0/docs/`
- Phase 1: `docs/phase1/`
- Architecture: `docs/architecture/`
