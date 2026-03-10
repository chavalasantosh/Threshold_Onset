# Phase 7: Role Emergence

**Enterprise Implementation - ✅ COMPLETE**

## Purpose

Discover functional roles from meaning clusters using quantile-based assignment.

## Core Principle

**Roles = Functional Behaviors Under Pressure**

Not POS labels. **Functional roles** from cluster properties.

## Key Components (All Corrections Applied)

1. **Cluster Property Computation**: Average properties per cluster
2. **Quantile-Based Assignment**: Emergent thresholds (not hand-chosen)
3. **Binder Derivation**: Derived from topology (not default)
4. **Unclassified Role**: For clusters that don't match any role

## Implementation Status

✅ **IMPLEMENTED**

All corrections applied:
- ✅ Quantile-based thresholds (not hand-chosen)
- ✅ Binder derived from topology (betweenness, edge_delta_variance)
- ✅ Unclassified role (not default binder)

## Files

- `role_emergence.py` - Main engine (✅ Complete)
- `role_assigner.py` - Role assignment with quantiles (✅ Complete)
- `properties.py` - Cluster property computation (✅ Complete)

## Usage

```python
from threshold_onset.semantic.phase7 import RoleEmergenceEngine
from threshold_onset.semantic.phase6 import MeaningDiscoveryEngine
from threshold_onset.semantic.phase5 import ConsequenceFieldEngine

# Build consequence field (Phase 5)
consequence_field = consequence_engine.build()

# Discover meaning (Phase 6)
meaning_map = meaning_engine.discover()

# Emerge roles (Phase 7)
role_engine = RoleEmergenceEngine(
    meaning_map=meaning_map,
    consequence_field=consequence_field,
    continuation_observer=observer  # Optional, for binder computation
)
roles = role_engine.emerge()

# Get role for symbol
role = role_engine.get_role(symbol)

# Get role properties
properties = role_engine.get_role_properties('anchor')
print(f"Anchor avg_survival: {properties['avg_survival']:.3f}")

# Save
role_engine.save('roles.json')
```

## Functional Roles

Roles discovered (not imported):

- **anchor**: High survival, low entropy, high concentration
- **driver**: High k_reach, high out_degree
- **gate**: Low out_degree, high refusal_rate
- **binder**: High betweenness, high edge_delta_variance (derived from topology)
- **terminator**: Low survival, high refusal_rate
- **unclassified**: Doesn't match any role (not default binder)

## Dependencies

- Phase 5: Consequence Field (required)
- Phase 6: Meaning Discovery (required)
- ContinuationObserver (optional, for binder computation)

## Output

`roles.json` with:
- `symbol_to_role`: Mapping of symbol/identity -> role
- `cluster_roles`: Mapping of cluster_id -> role
- `role_properties`: Properties for each role

## Algorithm

1. **Compute Properties**: Average properties for each cluster
2. **Compute Quantiles**: Emergent thresholds from data
3. **Assign Roles**: Match clusters to roles using quantiles
4. **Derive Binder**: Compute binder from topology (if observer available)

## Testing

See `tests/test_phase7.py` (to be implemented)

---

**See CORRECTIONS_APPLIED.md for quantile-based assignment details.**
