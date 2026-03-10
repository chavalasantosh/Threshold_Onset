# Source Code (`threshold_onset/`)

This directory contains all source code for the THRESHOLD_ONSET project.

**Note:** This package was renamed from `src/` to `threshold_onset/` to follow Python package naming conventions.

## Structure

```
src/
├── phase0/          # Phase 0 (THRESHOLD_ONSET) — FROZEN
├── phase1/          # Phase 1 (SEGMENTATION) — COMPLETE
├── phase2/          # Phase 2 (IDENTITY) — COMPLETE
├── phase3/          # Phase 3 (RELATION) — FROZEN
├── phase4/          # Phase 4 (SYMBOL) — UNBLOCKED (ready for implementation)
└── tools/           # Version control and utility tools
```

## Organization Principle

Each phase has its own directory with:
- Implementation code (`.py` files)
- Documentation (`docs/` subdirectory)
- README.md explaining the phase

## Phase Model

The project follows a strict phase model:
- **Phase 0** (FROZEN): THRESHOLD_ONSET - Action before Knowledge
- **Phase 1** (COMPLETE): SEGMENTATION - Segmentation without naming
- **Phase 2** (COMPLETE): IDENTITY - Identity without naming (multi-run)
- **Phase 3** (FROZEN): RELATION - Relation without naming
- **Phase 4** (UNBLOCKED): SYMBOL - Symbol assignment (ready for implementation)

## Code Standards

- Python standard library only (except version control tools)
- Clean, minimal code
- No third-party dependencies in core logic
- Phase boundaries strictly enforced
- Each phase operates independently

## Documentation

Each phase directory contains:
- `docs/` - Phase-specific documentation
- `README.md` - Phase overview and usage

See individual phase directories for details.
