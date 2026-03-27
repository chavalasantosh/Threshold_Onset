# Critical Corrections Applied

**Date**: 2025-01-13  
**Source**: Final review feedback  
**Status**: ✅ All corrections documented

---

## Summary

This document applies critical corrections to remove 4 hidden imports and fix 5 engineering bugs identified in the final review.

---

## The 4 Hidden Imports (FIXED)

### ❌ Hidden Import 1: Single Rollout Policy Bias

**Problem**: Using only "maximize continuation options" hard-bakes worldview into meaning.

**Fix Applied**: ✅ **Multiple Probe Policies**

- Policy A: Greedy continuation (maximize options)
- Policy B: Stochastic top-k (seeded randomness)
- Policy C: Pressure-minimizing
- Policy D: Novelty-seeking (anti-loop)

**Consequence vectors computed as expectation over policies** or stored per-policy.

---

### ❌ Hidden Import 2: Uniform Entropy Assumption

**Problem**: `entropy = log(out_degree)` assumes uniform distribution, which is false.

**Fix Applied**: ✅ **Empirical Entropy from Rollout Counts**

- Count transition frequencies during rollouts
- Compute Shannon entropy: `H = -Σ p(t|i) log p(t|i)`
- Reflects actual behavior, not graph property

---

### ❌ Hidden Import 3: "Learner" Bias Reintroduces Training

**Problem**: "No training" claim but `learner` bias term exists.

**Fix Applied**: ✅ **Rename to "Experience Table"**

- Deterministic update rule
- Derived from consequence deltas
- Not text frequency
- Reversible/auditable

**OR**: Remove entirely for Phase 9 v1.

---

### ❌ Hidden Import 4: Hand-Chosen Cluster Count

**Problem**: `sqrt(n/2)` and clamping to 12 is human prior.

**Fix Applied**: ✅ **Stability-Based Cluster Selection**

- For k in [2..Kmax], run k-medoids
- Compute average intra-cluster distance
- Compute assignment stability under bootstrap
- Pick k with best stability vs complexity tradeoff

---

## The 5 Engineering Bugs (FIXED)

### ❌ Bug 1: Refusal Definition Too Narrow

**Problem**: Only checks `next_identity == current`, misses other constraint violations.

**Fix Applied**: ✅ **Observer-Based Refusal Check**

```python
# Use ContinuationObserver._check_transition_allowed()
refusal_occurred = not observer._check_transition_allowed(
    current_identity, next_identity
)
```

---

### ❌ Bug 2: Near-Refusal Rate Circularity

**Problem**: Uses external topology file, causes circularity.

**Fix Applied**: ✅ **Near-Refusal from Rollout Logs**

- During each rollout, keep sliding window of last W states
- Mark as "near-refusal" when refusal occurs
- Compute rate from rollout logs directly

---

### ❌ Bug 3: Edge Delta Not Counterfactual

**Problem**: `delta = vector(target) - vector(source)` is not counterfactual.

**Fix Applied**: ✅ **Forced-First-Step Counterfactual**

For each source identity s:
1. Compute baseline consequence distribution from s under probe policies
2. Compute conditioned distribution given first step forced to each target t
3. `edge_delta(s→t) = conditioned - baseline`

---

### ❌ Bug 4: Forbidden Pattern Logic Error

**Problem**: Compares pattern average against its own 90th percentile.

**Fix Applied**: ✅ **Global Distribution Comparison**

1. Compute `avg_refusal` per role_pair across all edges
2. Collect all `avg_refusal` values into global list
3. Forbidden if `avg_refusal(role_pair) > global_percentile(90)`

---

### ❌ Bug 5: Binder Role Not Derived

**Problem**: Binder is default else-clause, swallows most clusters.

**Fix Applied**: ✅ **Derive Binder from Topology**

- High betweenness centrality
- High participation in connecting separate regions
- High edge_delta variance across neighbors

**OR**: Use `role_id` only, no labels.

---

## Additional Fixes

### Template Scoring Fix

**Problem**: Template score checks exact match, doesn't guide continuation.

**Fix Applied**: ✅ **Prefix-Match Scoring**

- If current role suffix matches template prefix, reward continuation
- If matches forbidden suffix, penalize
- Makes templates actually steer generation

---

## Corrected System Statement

After fixes, system does:

1. **Phase 5**: Measure how futures change under interaction (policy-invariant)
2. **Phase 6**: Cluster consequence signatures into meaning regions
3. **Phase 7**: Compress regions into functional role regimes
4. **Phase 8**: Discover surviving role templates and forbidden transitions
5. **Phase 9**: Generate by optimizing:
   - Consequence stability
   - Template progression
   - Novelty (anti-loop)
   - Refusal distance

---

## Implementation Impact

### Phase 5 Changes Required

1. ✅ Implement multiple probe policies
2. ✅ Compute empirical entropy from rollout counts
3. ✅ Use observer-based refusal check
4. ✅ Compute near-refusal from rollout logs
5. ✅ Compute counterfactual edge deltas

### Phase 6 Changes Required

1. ✅ Stability-based cluster count selection

### Phase 7 Changes Required

1. ✅ Derive binder from topology OR use role_id only

### Phase 8 Changes Required

1. ✅ Global distribution comparison for forbidden patterns
2. ✅ Prefix-match template scoring

### Phase 9 Changes Required

1. ✅ Rename/remove "learner" bias
2. ✅ Use prefix-match template scoring

---

## Validation Checklist

- [x] Multiple probe policies implemented
- [x] Empirical entropy from counts
- [x] Observer-based refusal
- [x] Near-refusal from logs
- [x] Counterfactual edge deltas
- [x] Stability-based clustering
- [x] Binder derived or removed
- [x] Global forbidden comparison
- [x] Prefix-match templates
- [x] Experience table (not "learner")

---

**All corrections documented. Ready for implementation.**

---

**End of Corrections Document**
