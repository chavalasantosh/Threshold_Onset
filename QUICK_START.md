# THRESHOLD_ONSET - Quick Start Guide

## Golden path (read this first)

1. `pip install -e ".[dev]"` from the repo root  
2. `python scripts/dev_check.py` — must pass before assuming something is “broken”  
3. Read **`docs/architecture/GOLDEN_PATH.md`** for one clear mental model and command table  

Then continue below for full pipeline runs.

## 🚀 Getting Started in 5 Minutes

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/chavalasantosh/THRESHOLDONSET.git
cd THRESHOLDONSET

# Install (optional - core system uses stdlib only)
pip install -e .
```

### 2. Run the System

**Full project (recommended):**
```bash
set PYTHONIOENCODING=utf-8
python main.py
```

**Or equivalent:**
```bash
python run_all.py
```

**Quick check with your text:**
```bash
python main.py --check "Your text here"
```

**Complete pipeline:**
```bash
python integration/run_complete.py
```

This executes all phases:
- Phase 0: Action → residue
- Phase 1: Boundaries without identity
- Phase 2: Identity survives across runs
- Phase 3: Relations persist and stabilize
- Phase 4: Pure aliasing layer
- Phases 5-9: Semantic discovery, fluency, structural decoder

### 3. Understand the Output

The system produces numerical outputs showing:
- **Residue counts** (Phase 0)
- **Boundary positions** (Phase 1)
- **Persistent segments** (Phase 2)
- **Relation graphs** (Phase 3)
- **Symbol aliases** (Phase 4)

### 4. Explore Configuration

Pipeline parameters are in `integration/run_complete.py`. See `docs/EXECUTION.md` for full run instructions.

### 5. Read the Documentation

- **Quick Overview**: [`README.md`](README.md)
- **Project Structure**: [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)
- **Simple Story**: [`docs/simple/PHASE0_TO_PHASE3_STORY.md`](docs/simple/PHASE0_TO_PHASE3_STORY.md)

## 📖 Next Steps

1. **Run with different parameters** - Edit `tokenization_method` and `num_runs` in `integration/run_complete.py`
2. **Run tests** - Validate system behavior:
   ```bash
   python run_all.py
   python -m pytest tests/ threshold_onset/semantic/tests/
   ```
3. **Read phase documentation** - Each phase has detailed docs in `threshold_onset/phaseX/phaseX/`
4. **Explore examples** - Check `santok_complete/examples/` for tokenization examples

## 🎯 Key Concepts

- **Phase 0**: Actions produce residues (structureless outputs)
- **Phase 1**: Patterns emerge from residues (boundaries, clusters)
- **Phase 2**: Identities persist across runs (same patterns recognized)
- **Phase 3**: Relations connect identities (how patterns interact)
- **Phase 4**: Symbols alias identities/relations (pure mapping, no meaning)
- **Phases 5-9**: Semantic discovery, fluency, structural decoder (symbol → token)

**Core Principle**: Structure emerges before language. Action happens before knowledge.

## ⚠️ Important Notes

- **All phases (0-9), decoder, integration are FROZEN** - See [PROJECT_FREEZE.md](PROJECT_FREEZE.md)
- **Standard library only** - No external dependencies required for core system
- **Python 3.8+** - Minimum Python version required

## 🆘 Need Help?

- Check [`README.md`](README.md) for detailed documentation
- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines
- Review phase-specific docs in `threshold_onset/phaseX/phaseX/`

---

**Remember**: This system proves that structure can exist and work together **BEFORE** anyone gives it names or assigns meaning.
