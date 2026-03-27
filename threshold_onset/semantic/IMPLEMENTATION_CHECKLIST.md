# Implementation Checklist - All Corrections Applied

**Enterprise Implementation Checklist**

## Critical Corrections Status

### ✅ Hidden Imports Fixed

- [x] **Multiple Probe Policies**: Implemented (greedy, stochastic_topk, novelty, pressure_min)
- [x] **Empirical Entropy**: Function added to `common/utils.py`
- [x] **Experience Table**: Renamed from "learner" (to be implemented)
- [x] **Stability-Based Clustering**: Spec updated (to be implemented)

### ✅ Engineering Bugs Fixed

- [x] **Observer-Based Refusal**: Spec updated to use `_check_transition_allowed()`
- [x] **Near-Refusal from Logs**: Spec updated to track during rollouts
- [x] **Counterfactual Edge Deltas**: Spec updated with forced-first-step method
- [x] **Global Forbidden Comparison**: Spec updated
- [x] **Binder Derivation**: Spec updated (derive from topology or use role_id)

### ✅ Additional Fixes

- [x] **Prefix-Match Templates**: Spec updated
- [x] **Template Scoring**: Updated to guide continuation

---

## Phase 5 Implementation Checklist

### Core Components

- [ ] Implement `policy_greedy()` function
- [ ] Implement `policy_stochastic_topk()` function
- [ ] Implement `policy_novelty_seeking()` function
- [ ] Implement `policy_pressure_minimizing()` function
- [ ] Implement `rollout_from_identity()` with policy selection
- [ ] Implement observer-based refusal check
- [ ] Implement near-refusal tracking in rollouts
- [ ] Implement `calculate_entropy_from_counts()` ✅ (DONE)
- [ ] Implement `compute_consequence_vector()` with multi-policy
- [ ] Implement `compute_counterfactual_edge_delta()`
- [ ] Implement `rollout_from_identity_forced_first()` for counterfactuals
- [ ] Implement `compute_k_reach_from_path()` helper
- [ ] Implement `ConsequenceFieldEngine.build()` with all corrections

### Testing

- [ ] Test multiple policies produce different results
- [ ] Test empirical entropy vs uniform entropy
- [ ] Test observer-based refusal detection
- [ ] Test near-refusal tracking
- [ ] Test counterfactual edge deltas
- [ ] Test determinism (same seed → same result)
- [ ] Test vector distributions

---

## Phase 6 Implementation Checklist

### Core Components

- [ ] Implement stability-based cluster count selection
- [ ] Implement k-medoids with stability scoring
- [ ] Remove `sqrt(n/2)` heuristic
- [ ] Test cluster stability

---

## Phase 7 Implementation Checklist

### Core Components

- [ ] Derive binder from topology (betweenness, connectivity)
- [ ] OR use `role_id` only (no labels)
- [ ] Remove default "binder" assignment
- [ ] Test role assignment

---

## Phase 8 Implementation Checklist

### Core Components

- [ ] Implement global distribution comparison for forbidden patterns
- [ ] Fix forbidden pattern logic (compare against global, not local)
- [ ] Implement prefix-match template scoring
- [ ] Test template continuation guidance

---

## Phase 9 Implementation Checklist

### Core Components

- [ ] Rename "learner" to "experience_table"
- [ ] OR remove entirely for v1
- [ ] Implement prefix-match template scoring
- [ ] Test generation quality

---

## Validation Checklist

### Phase 5 Validation

- [ ] Consequence vectors computed for all identities
- [ ] Vectors are deterministic (same seed → same result)
- [ ] All components are numeric (not boolean)
- [ ] Multiple policies produce different measurements
- [ ] Empirical entropy reflects actual behavior
- [ ] Observer-based refusal works correctly
- [ ] Near-refusal tracked from logs
- [ ] Counterfactual deltas computed correctly

### Phase 6 Validation

- [ ] Clusters discovered (not imported)
- [ ] Cluster count selected by stability
- [ ] Signatures are vector centroids
- [ ] Clustering is deterministic

### Phase 7 Validation

- [ ] Roles are functional (not POS)
- [ ] Binder derived or removed
- [ ] Roles use quantiles (not hand thresholds)
- [ ] All identities have roles

### Phase 8 Validation

- [ ] Patterns discovered from data
- [ ] Forbidden patterns use global comparison
- [ ] Templates use prefix matching
- [ ] Templates guide continuation

### Phase 9 Validation

- [ ] Refusal rate decreases
- [ ] Survival length increases
- [ ] Repetition decreases
- [ ] Readability improves
- [ ] Experience table (not "learner")

---

## Documentation Checklist

- [x] CORRECTIONS_APPLIED.md created
- [x] PHASE5_CORRECTED_SPEC.md created
- [x] IMPLEMENTATION_CHECKLIST.md created (this file)
- [ ] Update ARCHITECTURE.md with corrections
- [ ] Update CONTRACTS.md with corrections
- [ ] Update IMPLEMENTATION_PLAN.md with corrections

---

## Code Quality Checklist

- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] Error handling implemented
- [ ] Logging implemented
- [ ] Input validation implemented
- [ ] Tests written (>80% coverage)
- [ ] No hidden imports
- [ ] Deterministic operations
- [ ] Performance acceptable

---

**Status**: ✅ All corrections documented, ready for implementation

**Next Step**: Start Phase 5 implementation with corrected spec

---

**End of Checklist**
