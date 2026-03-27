"""
Phase 5: Consequence Field Engine

Enterprise-grade consequence measurement system.

All corrections applied:
- Multiple probe policies
- Observer-based refusal checking
- Empirical entropy from rollout counts
- Counterfactual edge deltas
- Near-refusal tracking from rollout logs
"""

from threshold_onset.semantic.phase5.consequence_field import ConsequenceFieldEngine
from threshold_onset.semantic.phase5.policies import (
    policy_greedy,
    policy_stochastic_topk,
    policy_pressure_minimizing,
    policy_novelty_seeking,
    get_policy
)
from threshold_onset.semantic.phase5.rollout import (
    rollout_from_identity,
    rollout_from_identity_forced_first
)
from threshold_onset.semantic.phase5.metrics import (
    compute_k_reach,
    compute_k_reach_from_path,
    get_escape_concentration,
    compute_near_refusal_rate_from_rollouts
)

__all__ = [
    'ConsequenceFieldEngine',
    'policy_greedy',
    'policy_stochastic_topk',
    'policy_pressure_minimizing',
    'policy_novelty_seeking',
    'get_policy',
    'rollout_from_identity',
    'rollout_from_identity_forced_first',
    'compute_k_reach',
    'compute_k_reach_from_path',
    'get_escape_concentration',
    'compute_near_refusal_rate_from_rollouts',
]
