# Architecture (`docs/architecture/`)

This directory contains system architecture and design documentation.

## Contents

### `ARCHITECTURE.md`
Complete system architecture documentation:
- Project structure
- Phase model
- Code organization
- File structure
- Design principles

## Purpose

This documentation explains:
1. How the system is organized
2. How phases interact
3. How code is structured
4. Design principles and patterns

## Architecture Principles

1. **Phase Model** - Strict phase boundaries
2. **Co-location** - Documentation with code
3. **Minimal Dependencies** - Standard library only
4. **Clean Structure** - Clear organization
5. **Frozen Phases** - Completed phases cannot be modified

## Project Structure

```
THRESHOLD_ONSET/
├── main.py              # Entry point
├── src/                 # Source code
│   ├── phase0/          # Phase 0 (frozen)
│   ├── phase1/          # Phase 1 (future)
│   └── tools/           # Utilities
├── docs/                # Documentation
│   ├── axioms/          # Core constraints
│   ├── architecture/    # This directory
│   ├── phase1/          # Phase 1 docs
│   └── history/         # Project history
└── versions/            # Version snapshots
```

## Related Documentation

- Axioms: `docs/axioms/`
- Phase 0: `src/phase0/docs/`
- Phase 1: `docs/phase1/`
