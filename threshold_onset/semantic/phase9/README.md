# Phase 9: Fluency Generator

**Enterprise Implementation - ✅ COMPLETE**

## Purpose

Generate fluent sequences using stability + novelty + templates.

## Core Principle

**Fluency = Stability + Novelty + Template Satisfaction**

Not just low entropy. **Balanced scoring**.

## Key Components (All Corrections Applied)

1. **Stability Scoring**: From consequence field (survival, entropy, refusal)
2. **Template Satisfaction**: Prefix-match scoring (CORRECTED)
3. **Novelty Constraint**: Anti-loop penalty
4. **Experience Table**: Derived from consequence deltas (CORRECTED: not "learner")

## Implementation Status

✅ **IMPLEMENTED**

All corrections applied:
- ✅ Experience table (not "learner")
- ✅ Prefix-match template scoring
- ✅ Stability + Novelty + Template balance

## Files

- `fluency_generator.py` - Main generator (✅ Complete)
- `scoring.py` - Scoring functions (✅ Complete)

## Usage

```python
from threshold_onset.semantic.phase9 import FluencyGenerator
from threshold_onset.semantic.phase5 import ConsequenceFieldEngine
from threshold_onset.semantic.phase7 import RoleEmergenceEngine
from threshold_onset.semantic.phase8 import ConstraintDiscoveryEngine

# Build all previous phases
consequence_field = consequence_engine.build()
meaning_map = meaning_engine.discover()
roles = role_engine.emerge()
constraints = constraint_engine.discover()

# Generate fluent text
generator = FluencyGenerator(
    consequence_field=consequence_field,
    roles=roles,
    constraints=constraints,
    phase3_relations=phase3_metrics,
    phase4_symbols=phase4_output,
    continuation_observer=observer
)

# Build experience table
generator.build_experience_table()

# Generate sequence
sequence = generator.generate(start_symbol=0, length=50, seed=42)

# Generate text (if symbol_to_text mapping available)
text = generator.generate_text(
    start_symbol=0,
    length=50,
    symbol_to_text=symbol_to_text,
    seed=42
)
```

## Scoring Components

### Stability Score (40%)
- Survival probability
- Entropy reduction
- Refusal distance

### Template Score (30%)
- Prefix-match with templates
- Weighted by frequency

### Experience Bias (20%)
- Derived from consequence deltas
- Positive survival_delta = good experience

### Novelty Penalty (10%)
- Anti-loop constraint
- Penalizes recent repetition

## Dependencies

- Phase 5: Consequence Field (required)
- Phase 7: Role Emergence (required)
- Phase 8: Constraint Discovery (required)
- ContinuationObserver (required)

## Output

- Symbol sequence: List of symbol IDs
- Text sequence: If symbol_to_text mapping provided

## Algorithm

1. **Score Transitions**: Stability + Template + Experience - Novelty
2. **Select Best**: Highest scoring transition
3. **Update State**: Add to sequence, update role sequence
4. **Repeat**: Until desired length or no valid transitions

## Testing

See `tests/test_phase9.py` (to be implemented)

---

**See CORRECTIONS_APPLIED.md for experience table and prefix-match details.**
