# Documentation (`docs/`)

This directory contains all project documentation, organized by category.

## Structure

```
docs/
├── axioms/              # Core axioms and design constraints
├── architecture/        # System architecture and design
├── phase1/             # Phase 1 (SEGMENTATION) documentation
├── phase3/             # Phase 3 (RELATION) freeze documentation
├── history/             # Project history and changes
├── PHASE_STATUS_CANONICAL.md  # Authoritative phase status
└── README.md           # This file
```

## Organization Principle

Documentation is organized by:
- **Category** (axioms, architecture, phases)
- **Purpose** (design, implementation, history)
- **Phase** (phase-specific documentation)

**Note:** Phase 0 documentation is co-located with code in `threshold_onset/phase0/docs/`

## Contents

### `axioms/`
Core non-negotiable design constraints:
- `AXIOMS.md` - Complete axiom definitions and phase boundaries

### `architecture/`
System architecture and design:
- `ARCHITECTURE.md` - Complete system architecture

### `phase1/`
Phase 1 (SEGMENTATION) documentation:
- `PHASE1_TRANSITION.md` - Transition rules from Phase 0 to Phase 1
- `PHASE1_IMPLEMENTATION_PROMPT_FINAL.md` - Corrected implementation prompt
- `PHASE1_IMPLEMENTATION_PROMPT.md` - Original implementation prompt (reference)

### `phase3/`
Phase 3 (RELATION) freeze documentation:
- `PHASE3_FREEZE.md` - Canonical freeze declaration (FROZEN FOREVER)
- `README.md` - Phase 3 documentation overview

### Status Documents
- `PHASE_STATUS_CANONICAL.md` - Authoritative, non-negotiable phase status
- `PHASE_STATUS_ACCURATE.md` - Accurate phase status (superseded by canonical)

### `history/`
Project history and change logs:
- `WORK_LOG.md` - Development work log
- `CORRECTIONS_APPLIED.md` - Summary of corrections applied

## Documentation Standards

- Each document has a clear purpose
- Documents are organized by phase and category
- Phase-specific docs are co-located with code when possible
- All documentation respects phase boundaries

## Related Documentation

- Phase 0 docs: `threshold_onset/phase0/docs/`
- Tools docs: `threshold_onset/tools/docs/`
- Root README: `README.md`
