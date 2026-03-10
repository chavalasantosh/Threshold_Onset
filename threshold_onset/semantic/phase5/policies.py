"""
Probe Policies for Consequence Field Measurement

Enterprise-grade policy implementations for rollout-based measurement.

Multiple policies ensure policy-invariant consequence measurement.
"""

import random
from typing import Optional, Set, List, Dict, Any
import logging

logger = logging.getLogger('threshold_onset.semantic.phase5')


def policy_greedy(
    current_identity: str,
    observer: Any,  # ContinuationObserver
    seed: Optional[int] = None
) -> Optional[str]:
    """
    Policy A: Greedy Continuation
    
    Select next identity that maximizes continuation options.
    Deterministic tie-breaking.
    
    Args:
        current_identity: Current identity hash
        observer: ContinuationObserver instance
        seed: Random seed (unused for greedy, kept for interface consistency)
        
    Returns:
        Next identity hash, or None if no allowed transitions
    """
    allowed = observer.adjacency.get(current_identity, set())
    if not allowed:
        return None
    
    scores = {}
    for target in allowed:
        target_futures = len(observer.adjacency.get(target, set()))
        scores[target] = target_futures
    
    if not scores:
        return None
    
    best_score = max(scores.values())
    candidates = [t for t, s in scores.items() if s == best_score]
    
    # Deterministic tie-breaking (sorted)
    return sorted(candidates)[0]


def policy_stochastic_topk(
    current_identity: str,
    observer: Any,  # ContinuationObserver
    k: int = 3,
    seed: Optional[int] = None
) -> Optional[str]:
    """
    Policy B: Stochastic Top-K
    
    Select randomly from top-k options (seeded for determinism).
    
    Args:
        current_identity: Current identity hash
        observer: ContinuationObserver instance
        k: Number of top options to consider
        seed: Random seed for deterministic selection
        
    Returns:
        Next identity hash, or None if no allowed transitions
    """
    allowed = observer.adjacency.get(current_identity, set())
    if not allowed:
        return None
    
    scores = {}
    for target in allowed:
        target_futures = len(observer.adjacency.get(target, set()))
        scores[target] = target_futures
    
    if not scores:
        return None
    
    # Get top-k
    sorted_targets = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_k = sorted_targets[:min(k, len(sorted_targets))]
    
    if not top_k:
        return None
    
    # Seeded random selection
    if seed is not None:
        random.seed(seed)
    
    selected = random.choice([t for t, _ in top_k])
    return selected


def policy_pressure_minimizing(
    current_identity: str,
    observer: Any,  # ContinuationObserver
    topology_data: Dict[int, Dict[str, Any]],
    seed: Optional[int] = None
) -> Optional[str]:
    """
    Policy C: Pressure-Minimizing
    
    Select next identity that minimizes pressure (if topology data available).
    Falls back to greedy if no topology data.
    
    Args:
        current_identity: Current identity hash
        observer: ContinuationObserver instance
        topology_data: Topology data dict (symbol -> topology info)
        seed: Random seed (unused, kept for interface consistency)
        
    Returns:
        Next identity hash, or None if no allowed transitions
    """
    allowed = observer.adjacency.get(current_identity, set())
    if not allowed:
        return None
    
    scores = {}
    has_pressure_data = False
    
    for target in allowed:
        # Get pressure from topology (if available)
        target_symbol = observer._identity_hash_to_symbol(target)
        if target_symbol is not None and target_symbol in topology_data:
            pressure = topology_data[target_symbol].get('pressure', 0.0)
            scores[target] = -pressure  # Minimize
            has_pressure_data = True
        else:
            # Fallback: use continuation options
            target_futures = len(observer.adjacency.get(target, set()))
            scores[target] = target_futures
    
    if not scores:
        return None
    
    if not has_pressure_data:
        # No pressure data, fall back to greedy
        logger.debug("No pressure data, falling back to greedy policy")
        return policy_greedy(current_identity, observer, seed)
    
    best_score = max(scores.values())
    candidates = [t for t, s in scores.items() if s == best_score]
    return sorted(candidates)[0]


def policy_novelty_seeking(
    current_identity: str,
    observer: Any,  # ContinuationObserver
    recent_path: List[str],
    seed: Optional[int] = None
) -> Optional[str]:
    """
    Policy D: Novelty-Seeking
    
    Select next identity that avoids recent path (anti-loop).
    
    Args:
        current_identity: Current identity hash
        observer: ContinuationObserver instance
        recent_path: List of recent identity hashes (last N)
        seed: Random seed (unused, kept for interface consistency)
        
    Returns:
        Next identity hash, or None if no allowed transitions
    """
    allowed = observer.adjacency.get(current_identity, set())
    if not allowed:
        return None
    
    # Penalize recent identities (use all recent path, not just last 5)
    recent_set = set(recent_path) if recent_path else set()
    
    scores = {}
    for target in allowed:
        if target in recent_set:
            scores[target] = 0.0  # Penalize recent
        else:
            target_futures = len(observer.adjacency.get(target, set()))
            scores[target] = target_futures
    
    if not scores:
        return None
    
    best_score = max(scores.values())
    candidates = [t for t, s in scores.items() if s == best_score]
    
    if not candidates:
        # All penalized, fall back to greedy
        return policy_greedy(current_identity, observer, seed)
    
    return sorted(candidates)[0]


def get_policy(policy_name: str):
    """
    Get policy function by name.
    
    Args:
        policy_name: One of 'greedy', 'stochastic_topk', 'pressure_min', 'novelty'
        
    Returns:
        Policy function
        
    Raises:
        ValueError: If policy name not recognized
    """
    policies = {
        'greedy': policy_greedy,
        'stochastic_topk': policy_stochastic_topk,
        'pressure_min': policy_pressure_minimizing,
        'novelty': policy_novelty_seeking,
    }
    
    if policy_name not in policies:
        raise ValueError(
            f"Unknown policy: {policy_name}. "
            f"Available: {list(policies.keys())}"
        )
    
    return policies[policy_name]
