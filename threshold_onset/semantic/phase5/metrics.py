"""
Consequence Metrics Computation

Enterprise-grade metric computation for consequence vectors.
"""

import math
import logging
from typing import List, Dict, Any, Set, Optional

from threshold_onset.semantic.common.utils import mean

logger = logging.getLogger('threshold_onset.semantic.phase5')


def compute_k_reach_from_path(path: List[str], k: int) -> int:
    """
    Compute k-step reachable set size from path.
    
    Args:
        path: List of identity hashes in path
        k: k-step horizon
        
    Returns:
        Number of unique identities reachable within k steps
    """
    if len(path) < 2:
        return 0
    
    reachable = set()
    for i in range(len(path) - 1):
        # Check k steps ahead
        if i + k < len(path):
            reachable.add(path[i + k])
        # Also add immediate next step
        if i + 1 < len(path):
            reachable.add(path[i + 1])
    
    return len(reachable)


def compute_k_reach(
    identity_hash: str,
    continuation_observer: Any,  # ContinuationObserver
    k: int = 5
) -> int:
    """
    Compute k-step reachable set size using BFS.
    
    Args:
        identity_hash: Starting identity hash
        continuation_observer: ContinuationObserver instance
        k: k-step horizon
        
    Returns:
        Number of unique identities reachable within k steps
    """
    reachable = set()
    current_level = {identity_hash}
    
    for step in range(k):
        next_level = set()
        for node in current_level:
            outgoing = continuation_observer.adjacency.get(node, set())
            next_level.update(outgoing)
            reachable.update(outgoing)
        current_level = next_level
        if not current_level:
            break
    
    return len(reachable)


def get_escape_concentration(
    symbol: Optional[int],
    topology_data: Optional[Dict[int, Dict[str, Any]]] = None
) -> float:
    """
    Get escape concentration from topology data (if available).
    
    Args:
        symbol: Symbol ID
        topology_data: Optional topology data dict
        
    Returns:
        Escape concentration [0.0, 1.0], or 0.0 if not available
    """
    if symbol is None or topology_data is None:
        return 0.0
    
    if symbol not in topology_data:
        return 0.0
    
    return topology_data[symbol].get('escape_concentration', 0.0)


def compute_near_refusal_rate_from_rollouts(
    identity_hash: str,
    rollout_results: List[Any]  # List[RolloutResult]
) -> float:
    """
    Compute near-refusal rate from rollout logs.
    
    CORRECTED: Computes from actual rollout logs, not external file.
    
    Args:
        identity_hash: Identity hash to compute rate for
        rollout_results: List of RolloutResult objects
        
    Returns:
        Near-refusal rate [0.0, 1.0]
    """
    if not rollout_results:
        return 0.0
    
    total_visits = 0
    near_refusal_visits = 0
    
    for result in rollout_results:
        # Count visits to identity_hash in path
        visits_in_path = result.path_taken.count(identity_hash)
        total_visits += visits_in_path
        
        # Count if identity_hash is in near-refusal states
        # Handle None case (shouldn't happen, but defensive programming)
        if result.near_refusal_states is not None and identity_hash in result.near_refusal_states:
            near_refusal_visits += visits_in_path
    
    if total_visits == 0:
        return 0.0
    
    return near_refusal_visits / total_visits
