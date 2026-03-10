# THRESHOLD_ONSET - Project Structure

## Professional AI Architect-Grade Organization

```
THRESHOLD_ONSET/
├── threshold_onset/          # Main package (source code)
│   ├── __init__.py
│   ├── phase0/               # Phase 0: THRESHOLD_ONSET (FROZEN)
│   ├── phase1/               # Phase 1: SEGMENTATION (FROZEN)
│   ├── phase2/               # Phase 2: IDENTITY (FROZEN)
│   ├── phase3/               # Phase 3: RELATION (FROZEN)
│   ├── phase4/               # Phase 4: SYMBOL (FROZEN)
│   ├── tools/                # Version control tools
│   └── README.md
│
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_phase3_convergence.py
│   └── test_phase4_freeze.py
│
├── examples/                 # Example scripts
│   └── README.md
│
├── scripts/                  # Utility scripts
│   └── README.md
│
├── docs/                     # Project documentation
│   ├── axioms/               # Core design constraints
│   ├── architecture/         # System architecture
│   ├── simple/               # Non-technical explanations
│   ├── history/              # Project history
│   └── README.md
│
├── archive/                  # Archived materials
│   ├── backup_pre_cleanup_20260113/
│   └── reference/
│
├── santok_complete/         # Tokenization submodule
│   ├── core/                 # Core tokenization
│   ├── santok/               # Alternative implementation
│   ├── examples/             # Tokenization examples
│   └── tests/                # Tokenization tests
│
├── integration/              # Unified system (threshold_onset <-> santok)
│   ├── unified_system.py     # Main integration module
│   ├── example_unified.py    # Example usage
│   └── README.md             # Integration documentation
│
├── .github/                  # GitHub workflows
│   └── workflows/
│
├── versions/                 # Version snapshots (auto-generated)
│
├── setup.py                  # Package setup
├── pyproject.toml           # Modern Python project config
├── requirements.txt          # Dependencies
├── main.py                   # Primary entry point (10-step suite)
├── run_all.py                # Equivalent to main.py
├── main.bat                  # Windows: run main.py
├── run_all.bat               # Windows: run run_all.py
├── project_viewer.py         # Comprehensive project explorer
├── README.md                 # Main documentation
├── LICENSE                   # MIT License
├── PROJECT_STRUCTURE.md      # This file
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guidelines
└── QUICK_START.md           # Quick start guide
```

## Directory Descriptions

### `/threshold_onset` - Main Package
Contains all source code organized by phase. Each phase is self-contained with its own documentation.

**Note:** This directory was renamed from `src/` to `threshold_onset/` for professional package structure.

### `/tests` - Test Suite
All tests are consolidated here for easy discovery and execution.

### `/examples` - Example Scripts
Demonstration scripts showing how to use the system.

### `/scripts` - Utility Scripts
Development and maintenance utilities.

### `/docs` - Documentation
Comprehensive documentation including:
- Core axioms and constraints
- Architecture documentation
- Simple explanations for non-technical users
- Project history

### `/archive` - Archived Materials
Historical backups and reference materials preserved for record-keeping.

### `/santok_complete` - Tokenization Submodule
Standalone tokenization system with complete package structure.

### `/integration` - Unified System Integration
Experimental integration of threshold_onset with santok. Contains unified system code and documentation.

## Package Installation

After reorganization, the package structure follows Python best practices:

```bash
# Install in development mode
pip install -e .

# Package imports work as:
from threshold_onset.phase0.phase0 import phase0
from threshold_onset.phase1.phase1 import phase1
```

## Import Paths

All imports have been updated to use `threshold_onset` instead of `src`:

- ✅ `main.py` - Updated
- ✅ `tests/*.py` - Updated
- ✅ `setup.py` - Updated
- ✅ `pyproject.toml` - Updated
- ✅ `.github/workflows/*.yml` - Updated

## Migration Notes

**Changed:**
- `src/` → `threshold_onset/` (package rename)

**Moved:**
- `test_*.py` → `tests/`
- `backup_*/` → `archive/`
- `reference/` → `archive/`

**Created:**
- `examples/` - For example scripts
- `scripts/` - For utility scripts
- `archive/` - For historical materials
- `integration/` - For unified system work (threshold_onset <-> santok)

## Benefits of This Structure

1. **Standard Python Package Layout** - Follows PEP 518/517 conventions
2. **Clear Separation of Concerns** - Tests, docs, examples clearly separated
3. **Professional Organization** - Industry-standard structure
4. **Easy Discovery** - Intuitive directory names
5. **Scalable** - Easy to add new components

## Maintaining the Structure

- **Source code**: Always in `/threshold_onset`
- **Tests**: Always in `/tests`
- **Examples**: Always in `/examples`
- **Documentation**: Always in `/docs`
- **Archives**: Always in `/archive`
- **Integration work**: Always in `/integration`