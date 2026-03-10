"""
Rollout System for Consequence Field Measurement

Enterprise-grade rollout implementation with observer-based refusal checking
and empirical entropy tracking.
"""

import logging
from typing import Optional, List, Dict, Any
from collections import Counter

from threshold_onset.semantic.common.types import RolloutResult
from threshold_onset.semantic.common.utils import calculate_entropy_from_counts
from threshold_onset.semantic.phase5.policies import get_policy

logger = logging.getLogger('threshold_onset.semantic.phase5')


def rollout_from_identity(
    identity_hash: str,
    phase3_relations: Dict[str, Any],
    phase4_symbols: Dict[str, Any],
    continuation_observer: Any,  # ContinuationObserver
    policy: str = 'greedy',
    max_steps: int = 50,
    seed: Optional[int] = None,
    topology_data: Optional[Dict[int, Dict[str, Any]]] = None
) -> RolloutResult:
    """
    Run rollout from identity using specified policy.
    
    CORRECTED: Uses observer-based refusal check, not just self-loop check.
    Tracks near-refusal states and empirical entropy from transition counts.
    
    Args:
        identity_hash: Starting identity hash
        phase3_relations: Phase 3 relation metrics (for reference)
        phase4_symbols: Phase 4 symbol mappings (for reference)
        continuation_observer: ContinuationObserver instance
        policy: Policy name ('greedy', 'stochastic_topk', 'pressure_min', 'novelty')
        max_steps: Maximum rollout length
        seed: Random seed (for stochastic policies)
        topology_data: Optional topology data for pressure-minimizing policy
        
    Returns:
        RolloutResult with path, refusal, entropy trajectory, near-refusal states
    """
    policy_func = get_policy(policy)
    
    path = [identity_hash]
    pressure = 0.0
    entropy_values = []
    refusal_occurred = False
    near_refusal_states = []  # Track near-refusal
    transition_counts = Counter()  # For empirical entropy
    
    current = identity_hash
    recent_path = []
    
    for step in range(max_steps):
        # Get allowed next identities
        allowed = continuation_observer.adjacency.get(current, set())
        
        if not allowed:
            # Dead-end (different from refusal)
            break
        
        # Select next using policy
        try:
            if policy == 'pressure_min' and topology_data is not None:
                next_identity = policy_func(
                    current, continuation_observer, topology_data, seed
                )
            elif policy == 'novelty':
                next_identity = policy_func(
                    current, continuation_observer, recent_path, seed
                )
            elif policy == 'stochastic_topk':
                # Use step-specific seed for determinism
                step_seed = seed + step if seed is not None else None
                next_identity = policy_func(
                    current, continuation_observer, k=3, seed=step_seed
                )
            else:
                next_identity = policy_func(current, continuation_observer, seed)
        except Exception as e:
            logger.warning(f"Policy {policy} failed at step {step}: {e}")
            break
        
        if next_identity is None:
            break
        
        # CORRECTED: Check for refusal using observer (not just self-loop)
        transition_allowed = continuation_observer._check_transition_allowed(
            current, next_identity
        )
        
        if not transition_allowed:
            refusal_occurred = True
            # Mark recent states as near-refusal (CORRECTED)
            near_refusal_states.extend(recent_path[-3:])
            near_refusal_states.append(current)
            logger.debug(
                f"Refusal at step {step}: {current} -> {next_identity} "
                f"(near-refusal states: {len(near_refusal_states)})"
            )
            break
        
        # Track transition for empirical entropy (CORRECTED)
        transition_counts[(current, next_identity)] += 1
        
        # Update
        path.append(next_identity)
        recent_path.append(current)
        if len(recent_path) > 5:
            recent_path.pop(0)
        
        current = next_identity
        
        # Compute empirical entropy from transition counts (CORRECTED)
        current_transitions = [
            count for (src, tgt), count in transition_counts.items()
            if src == current
        ]
        if current_transitions:
            # Empirical entropy from actual transition frequencies
            entropy = calculate_entropy_from_counts(current_transitions)
        else:
            # Fallback: uniform entropy (if no transitions yet)
            from threshold_onset.semantic.common.utils import calculate_entropy_from_options
            entropy = calculate_entropy_from_options(len(allowed))
        
        entropy_values.append(entropy)
        
        # Measure pressure
        pressure += 1.0 / max(len(allowed), 1)
    
    return RolloutResult(
        survival_length=len(path) - 1,
        refusal_occurred=refusal_occurred,
        pressure_accumulated=pressure,
        entropy_trajectory=entropy_values,
        path_taken=path,
        # Always return a list, never None
        near_refusal_states = list(near_refusal_states) if near_refusal_states else []
    )


def rollout_from_identity_forced_first(
    source_hash: str,
    forced_target_hash: str,
    phase3_relations: Dict[str, Any],
    phase4_symbols: Dict[str, Any],
    continuation_observer: Any,  # ContinuationObserver
    policy: str = 'greedy',
    max_steps: int = 50,
    seed: Optional[int] = None
) -> RolloutResult:
    """
    Run rollout from source, but force first step to target.
    
    Used for counterfactual edge delta computation.
    
    Args:
        source_hash: Source identity hash
        forced_target_hash: Target identity hash (forced first step)
        phase3_relations: Phase 3 relation metrics
        phase4_symbols: Phase 4 symbol mappings
        continuation_observer: ContinuationObserver instance
        policy: Policy name for subsequent steps
        max_steps: Maximum rollout length
        seed: Random seed
        
    Returns:
        RolloutResult with forced first step
    """
    # Check if forced transition is allowed
    transition_allowed = continuation_observer._check_transition_allowed(
        source_hash, forced_target_hash
    )
    
    if not transition_allowed:
        # Forced transition not allowed - return refusal result
        return RolloutResult(
            survival_length=0,
            refusal_occurred=True,
            pressure_accumulated=0.0,
            entropy_trajectory=[],
            path_taken=[source_hash],
            near_refusal_states=[source_hash]
        )
    
    # Start with forced first step
    path = [source_hash, forced_target_hash]
    pressure = 0.0
    entropy_values = []
    refusal_occurred = False
    near_refusal_states = []
    transition_counts = Counter()
    
    current = forced_target_hash
    recent_path = [source_hash]
    
    # Continue rollout from forced target
    for step in range(1, max_steps):  # Start from step 1 (step 0 was forced)
        allowed = continuation_observer.adjacency.get(current, set())
        
        if not allowed:
            break
        
        # Select next using policy
        policy_func = get_policy(policy)
        
        try:
            if policy == 'stochastic_topk':
                step_seed = seed + step if seed is not None else None
                next_identity = policy_func(
                    current, continuation_observer, k=3, seed=step_seed
                )
            else:
                next_identity = policy_func(current, continuation_observer, seed)
        except Exception as e:
            logger.warning(f"Policy {policy} failed at step {step}: {e}")
            break
        
        if next_identity is None:
            break
        
        # Check for refusal
        transition_allowed = continuation_observer._check_transition_allowed(
            current, next_identity
        )
        
        if not transition_allowed:
            refusal_occurred = True
            near_refusal_states.extend(recent_path[-3:])
            near_refusal_states.append(current)
            break
        
        # Track transition
        transition_counts[(current, next_identity)] += 1
        
        path.append(next_identity)
        recent_path.append(current)
        if len(recent_path) > 5:
            recent_path.pop(0)
        
        current = next_identity
        
        # Compute empirical entropy
        current_transitions = [
            count for (src, tgt), count in transition_counts.items()
            if src == current
        ]
        if current_transitions:
            entropy = calculate_entropy_from_counts(current_transitions)
        else:
            from threshold_onset.semantic.common.utils import calculate_entropy_from_options
            entropy = calculate_entropy_from_options(len(allowed))
        
        entropy_values.append(entropy)
        pressure += 1.0 / max(len(allowed), 1)
    
    return RolloutResult(
        survival_length=len(path) - 1,
        refusal_occurred=refusal_occurred,
        pressure_accumulated=pressure,
        entropy_trajectory=entropy_values,
        path_taken=path,
        # Always return a list, never None
        near_refusal_states = list(near_refusal_states) if near_refusal_states else []
    )
