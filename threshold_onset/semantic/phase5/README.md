# Phase 5: Consequence Field Engine

**Enterprise Implementation - ✅ COMPLETE**

## Purpose

Measure how structures affect future possibilities through rollout-based measurement.

## Core Principle

**Meaning = Measurable Effect on Future Space Under Multiple Interaction Policies**

A structure's meaning is measured by how it changes future possibilities under different interaction policies, not by static graph topology.

## Key Components (All Corrections Applied)

1. **Multiple Probe Policies**: Greedy, Stochastic Top-K, Novelty-Seeking, Pressure-Minimizing
2. **Rollout System**: Controlled traversal with observer-based refusal checking
3. **k-Step Reachability**: Consistent horizon measurement
4. **Empirical Entropy**: From actual rollout transition counts (not uniform assumption)
5. **Survival Probability**: Rollout-based survival rate across policies
6. **Refusal Proximity**: Actual refusal events tracked from rollout logs
7. **Dead-End Risk**: Separate metric for zero-outgoing nodes
8. **Counterfactual Edge Deltas**: Forced-first-step method

## Implementation Status

✅ **IMPLEMENTED**

All corrections applied:
- ✅ Multiple probe policies
- ✅ Observer-based refusal check
- ✅ Empirical entropy from counts
- ✅ Counterfactual edge deltas
- ✅ Near-refusal from rollout logs

## Files

- `consequence_field.py` - Main engine (✅ Complete)
- `rollout.py` - Rollout measurement (✅ Complete)
- `metrics.py` - Metric computation (✅ Complete)
- `policies.py` - Probe policies (✅ Complete)

## Usage

```python
from threshold_onset.semantic.phase5 import ConsequenceFieldEngine
from integration.continuation_observer import ContinuationObserver

# Initialize observer
observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)

# Create engine
engine = ConsequenceFieldEngine(
    phase2_identities=phase2_metrics,
    phase3_relations=phase3_metrics,
    phase4_symbols=phase4_output,
    continuation_observer=observer
)

# Optional: Set topology data for pressure-minimizing policy
engine.set_topology_data(topology_data)

# Build consequence field
consequence_field = engine.build(k=5, num_rollouts=100, seed=42)

# Get vector for identity
vector = engine.get_vector(identity_hash)

# Get edge delta
delta = engine.get_delta((source_hash, target_hash))

# Save to file
engine.save('consequence_field.json')
```

## Dependencies

- Phases 2-4 (FROZEN)
- `ContinuationObserver` (existing)
- `escape_topology.py` (optional, for pressure-minimizing policy)

## Output

`consequence_field.json` with:
- Identity vectors (7 components each):
  - `out_degree`: Number of outgoing relations
  - `k_reach`: k-step reachable set size
  - `survival`: Survival probability [0.0, 1.0]
  - `entropy`: Empirical entropy (bits)
  - `escape_concentration`: Escape concentration [0.0, 1.0]
  - `near_refusal_rate`: Near-refusal rate [0.0, 1.0]
  - `dead_end_risk`: Dead-end risk [0.0, 1.0]
- Edge deltas (counterfactual):
  - `survival_delta`: Change in survival
  - `k_reach_delta`: Change in k-reach
  - `entropy_delta`: Change in entropy
  - `refusal_delta`: Change in refusal rate
- Metadata: k, num_rollouts, policies, etc.

## Testing

See `tests/test_phase5.py` (to be implemented)

---

**See PHASE5_CORRECTED_SPEC.md for detailed corrected specification.**
