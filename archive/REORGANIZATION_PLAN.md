# Project Reorganization Plan

## Target Professional Structure

```
THRESHOLD_ONSET/
├── threshold_onset/          # Main package (renamed from src/)
│   ├── __init__.py
│   ├── phase0/
│   ├── phase1/
│   ├── phase2/
│   ├── phase3/
│   ├── phase4/
│   └── tools/
│
├── tests/                    # All tests consolidated
│   ├── __init__.py
│   ├── test_phase3_convergence.py
│   └── test_phase4_freeze.py
│
├── examples/                 # Example scripts (new)
│   └── README.md
│
├── scripts/                  # Utility scripts (new)
│   └── README.md
│
├── docs/                     # Documentation (unchanged)
│
├── archive/                  # Archived materials (new)
│   ├── backup_pre_cleanup_20260113/
│   └── reference/
│
├── santok_complete/         # Tokenization submodule (unchanged)
│
├── .github/                  # GitHub workflows (unchanged)
│
├── versions/                 # Version snapshots (unchanged)
│
├── setup.py                  # Updated for new structure
├── pyproject.toml           # Updated for new structure
├── requirements.txt
├── main.py                   # Updated imports
├── README.md
├── LICENSE
└── ... (other root files)
```

## Changes Required

1. Rename `src/` → `threshold_onset/`
2. Move tests to `tests/`
3. Create `examples/` directory
4. Create `scripts/` directory  
5. Create `archive/` and move backup/reference there
6. Update all imports in codebase
7. Update setup.py and pyproject.toml
8. Update main.py
9. Update test files
10. Update .github workflows
11. Update documentation
