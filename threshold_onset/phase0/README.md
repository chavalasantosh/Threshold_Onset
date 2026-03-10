# Phase 0 — THRESHOLD_ONSET

**Status:** ✅ **FROZEN PERMANENTLY**

Phase 0 proves that **action can exist without knowledge**.

## Core Axiom

**कार्य (kārya) happens before ज्ञान (jñāna)**

Function stabilizes before knowledge appears.

## What Phase 0 Does

Phase 0 performs actions, collects opaque residues (traces), and repeats. It produces **only** three canonical outputs:

1. **Total residue count** - How many residues were collected
2. **Unique residue count** - How many unique residues exist
3. **Collision rate** - Rate of residue repetition

**Nothing else is allowed.**

## Files

### Core Implementation
- `phase0.py` - Main Phase 0 pipeline (frozen, do not modify)
  - Function: `phase0(actions, steps)` - yields (trace, count, step_count)

### Constraint Reminders (Placeholders)
- `action.py` - Docstring reminder about action constraints
- `trace.py` - Docstring reminder about trace constraints
- `repetition.py` - Docstring reminder about repetition constraints

**Note:** These placeholder files are not operational code. They serve as constraint reminders for future phases.

## Usage

```python
from phase0.phase0 import phase0
import random

# Define raw actions (no labels, no meaning)
actions = [
    lambda: random.random(),  # Structureless residue
    lambda: random.random(),  # Structureless residue
]

# Collect traces
traces = []
for trace, count, step in phase0(actions, steps=10):
    traces.append(trace)

# Calculate canonical outputs
total_count = len(traces)
unique_count = len(set(traces))
collision_rate = 1.0 - (unique_count / total_count) if total_count > 0 else 0.0
```

## What Phase 0 Allows

✅ Action  
✅ Opaque residue / trace  
✅ Repetition  
✅ Persistence  
✅ Survival (count-based only)

## What Phase 0 Forbids

❌ Symbols, labels, names, IDs  
❌ Meaning, interpretation  
❌ Segmentation, distributions  
❌ Visualization, plots, coordinates  
❌ Statistics beyond counts  
❌ Min/max, ranges, bins  
❌ Real-time narration

## Output Contract

**Returns:** Opaque residue list (internal handoff to Phase 1 only; not to be inspected or displayed)

**Prints:** Only 3 canonical values:
- Total residue count
- Unique residue count
- Collision rate

## Documentation

See `docs/` subdirectory for:
- Phase 0 verification and compliance documents
- Implementation details
- Transition rules to Phase 1

## Status

**Phase 0 is FROZEN.**

- ✅ Implemented
- ✅ Verified
- ✅ Compliant
- 🔒 **Cannot be modified**

Phase 0 serves as the foundation for Phase 1. It must remain unchanged.
