# Phase 8: Constraint Discovery

**Enterprise Implementation - ✅ COMPLETE**

## Purpose

Discover grammar-like constraints from role patterns.

## Core Principle

**Constraints = Role Patterns That Survive Pressure**

Not imported grammar. **Discovered patterns**.

## Key Components (All Corrections Applied)

1. **Role Sequence Extraction**: Convert symbol sequences to role sequences
2. **Pattern Mining**: Discover frequent role n-grams
3. **Global Forbidden Comparison**: Compare against global distribution (CORRECTED)
4. **Prefix-Match Templates**: Templates guide continuation (CORRECTED)

## Implementation Status

✅ **IMPLEMENTED**

All corrections applied:
- ✅ Global forbidden pattern comparison (not local percentile)
- ✅ Prefix-match template scoring (guides continuation)
- ✅ Discovered patterns (not imported)

## Files

- `constraint_discovery.py` - Main engine (✅ Complete)
- `pattern_miner.py` - Pattern mining (✅ Complete)
- `sequences.py` - Role sequence extraction (✅ Complete)

## Usage

```python
from threshold_onset.semantic.phase8 import ConstraintDiscoveryEngine
from threshold_onset.semantic.phase7 import RoleEmergenceEngine

# Emerge roles (Phase 7)
roles = role_engine.emerge()

# Discover constraints (Phase 8)
constraint_engine = ConstraintDiscoveryEngine(
    roles=roles,
    symbol_sequences=symbol_sequences,
    edge_deltas=consequence_field.edge_deltas,
    continuation_observer=observer,
    identity_to_symbol=identity_to_symbol
)
constraints = constraint_engine.discover()

# Get templates
templates = constraint_engine.get_templates()

# Check if pattern is forbidden
is_forbidden = constraint_engine.is_forbidden(('anchor', 'driver'))

# Compute template score (prefix-match)
current_roles = ['anchor', 'driver']
score = constraint_engine.compute_template_score(current_roles)

# Save
constraint_engine.save('constraints.json')
```

## Dependencies

- Phase 5: Consequence Field (for edge_deltas)
- Phase 7: Role Emergence (for roles)
- Symbol sequences (from Phase 2-4)

## Output

`constraints.json` with:
- `role_patterns`: Dictionary of pattern -> {frequency, length}
- `forbidden_patterns`: List of forbidden role patterns
- `templates`: List of valid templates

## Algorithm

1. **Extract Sequences**: Convert symbols to roles
2. **Mine Patterns**: Discover frequent n-grams
3. **Find Forbidden**: Compare against global distribution (CORRECTED)
4. **Build Templates**: Valid patterns become templates
5. **Prefix Matching**: Templates guide continuation (CORRECTED)

## Testing

See `tests/test_phase8.py` (to be implemented)

---

**See CORRECTIONS_APPLIED.md for global comparison and prefix-match details.**
