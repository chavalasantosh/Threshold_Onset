"""
Role Assignment from Cluster Properties

Enterprise-grade role assignment using quantiles (not hand thresholds).

CORRECTED: Uses quantiles for thresholds, derives binder from topology.
"""

import logging
from typing import Dict, List, Any, Optional, Set

from threshold_onset.semantic.common.utils import calculate_percentile, mean, variance
from threshold_onset.semantic.phase7.properties import compute_cluster_properties

logger = logging.getLogger('threshold_onset.semantic.phase7')


def compute_binder_properties(
    cluster_identities: List[str],
    identity_vectors: Dict[str, Any],
    continuation_observer: Any,
    edge_deltas: Dict[tuple, Dict[str, float]]
) -> Dict[str, float]:
    """
    Compute binder-specific properties from topology.
    
    CORRECTED: Binder derived from topology, not default.
    
    Binder properties:
    - betweenness_like: High participation in connecting regions
    - edge_delta_variance: High variance in edge deltas across neighbors
    - bridge_frequency: Frequency as bridge in paths
    
    Args:
        cluster_identities: List of identity hashes in cluster
        identity_vectors: Consequence vectors
        continuation_observer: ContinuationObserver instance
        edge_deltas: Edge deltas from Phase 5
        
    Returns:
        Dictionary of binder properties
    """
    if not cluster_identities:
        return {'betweenness_like': 0.0, 'edge_delta_variance': 0.0, 'bridge_frequency': 0.0}

    # Precompute incoming links and direct-edge lookup for bridge scoring.
    adjacency = continuation_observer.adjacency
    incoming_map: Dict[str, Set[str]] = {identity_hash: set() for identity_hash in adjacency}
    direct_edges: Set[tuple] = set()
    for src, targets in adjacency.items():
        for dst in targets:
            direct_edges.add((src, dst))
            incoming_map.setdefault(dst, set()).add(src)
    
    # Compute edge_delta variance for identities in cluster
    delta_variances = []
    for identity_hash in cluster_identities:
        # Get all outgoing edges from this identity
        outgoing = continuation_observer.adjacency.get(identity_hash, set())
        if not outgoing:
            continue
        
        # Get deltas for these edges
        deltas = []
        for target in outgoing:
            transition = (identity_hash, target)
            if transition in edge_deltas:
                delta = edge_deltas[transition]
                # Use absolute value of survival_delta as measure
                deltas.append(abs(delta.get('survival_delta', 0.0)))
        
        if deltas:
            delta_var = variance(deltas)
            delta_variances.append(delta_var)
    
    avg_delta_variance = mean(delta_variances) if delta_variances else 0.0
    
    # Simple betweenness-like: count how many identities have this as neighbor
    neighbor_counts = []
    for identity_hash in cluster_identities:
        outgoing = continuation_observer.adjacency.get(identity_hash, set())
        neighbor_counts.append(len(outgoing))
    
    avg_neighbor_count = mean(neighbor_counts) if neighbor_counts else 0.0

    # Bridge frequency: share of two-hop (incoming -> node -> outgoing) routes
    # where direct incoming->outgoing edge is absent, so node acts as a bridge.
    bridge_scores: List[float] = []
    for identity_hash in cluster_identities:
        incoming = incoming_map.get(identity_hash, set())
        outgoing = adjacency.get(identity_hash, set())
        if not incoming or not outgoing:
            continue

        possible_pairs = 0
        bridge_pairs = 0
        for src in incoming:
            for dst in outgoing:
                if src == dst or src == identity_hash or dst == identity_hash:
                    continue
                possible_pairs += 1
                if (src, dst) not in direct_edges:
                    bridge_pairs += 1

        if possible_pairs > 0:
            bridge_scores.append(bridge_pairs / possible_pairs)

    bridge_frequency = mean(bridge_scores) if bridge_scores else 0.0
    
    return {
        'betweenness_like': avg_neighbor_count,
        'edge_delta_variance': avg_delta_variance,
        'bridge_frequency': bridge_frequency
    }


def assign_roles_from_properties(
    clusters: Dict[str, List[str]],
    identity_vectors: Dict[str, Any],
    continuation_observer: Optional[Any] = None,
    edge_deltas: Optional[Dict[tuple, Dict[str, float]]] = None,
    percentile_high: int = 75,
    percentile_low: int = 25
) -> Dict[str, str]:
    """
    Assign functional roles from cluster properties.
    
    CORRECTED: Uses quantiles (not hand thresholds), derives binder from topology.
    
    Roles (functional, not POS):
    - anchor: high survival, low entropy, high concentration
    - driver: high k_reach, medium survival, high out_degree
    - gate: low out_degree, high refusal_rate, high influence
    - binder: high betweenness, high edge_delta_variance (derived from topology)
    - terminator: low survival, high refusal_rate
    - unclassified: doesn't match any role (not default binder)
    
    Args:
        clusters: Dictionary mapping cluster_id -> list of identity_hashes
        identity_vectors: Dictionary mapping identity_hash -> ConsequenceVector
        continuation_observer: Optional ContinuationObserver (for binder computation)
        edge_deltas: Optional edge deltas (for binder computation)
        percentile_high: High threshold percentile (default: 75)
        percentile_low: Low threshold percentile (default: 25)
        
    Returns:
        Dictionary mapping cluster_id -> role name
    """
    # Collect all properties
    all_survivals = []
    all_entropies = []
    all_concentrations = []
    all_refusal_rates = []
    all_k_reaches = []
    all_out_degrees = []
    
    cluster_properties = {}
    
    for cluster_id, cluster_identities in clusters.items():
        props = compute_cluster_properties(cluster_identities, identity_vectors)
        cluster_properties[cluster_id] = props
        
        if props:
            all_survivals.append(props['avg_survival'])
            all_entropies.append(props['avg_entropy'])
            all_concentrations.append(props['avg_concentration'])
            all_refusal_rates.append(props['avg_refusal_rate'])
            all_k_reaches.append(props['avg_k_reach'])
            all_out_degrees.append(props['avg_out_degree'])
    
    # Compute quantiles (emergent thresholds)
    quantiles = {}
    
    if all_survivals:
        quantiles['survival_high'] = calculate_percentile(all_survivals, percentile_high)
        quantiles['survival_low'] = calculate_percentile(all_survivals, percentile_low)
    else:
        quantiles['survival_high'] = 0.5
        quantiles['survival_low'] = 0.0
    
    if all_entropies:
        quantiles['entropy_high'] = calculate_percentile(all_entropies, percentile_high)
        quantiles['entropy_low'] = calculate_percentile(all_entropies, percentile_low)
    else:
        quantiles['entropy_high'] = 1.0
        quantiles['entropy_low'] = 0.0
    
    if all_concentrations:
        quantiles['concentration_high'] = calculate_percentile(all_concentrations, percentile_high)
    else:
        quantiles['concentration_high'] = 0.5
    
    if all_refusal_rates:
        quantiles['refusal_high'] = calculate_percentile(all_refusal_rates, percentile_high)
    else:
        quantiles['refusal_high'] = 0.5
    
    if all_k_reaches:
        quantiles['k_reach_high'] = calculate_percentile(all_k_reaches, percentile_high)
    else:
        quantiles['k_reach_high'] = 5.0
    
    if all_out_degrees:
        quantiles['out_degree_high'] = calculate_percentile(all_out_degrees, percentile_high)
        quantiles['out_degree_low'] = calculate_percentile(all_out_degrees, percentile_low)
    else:
        quantiles['out_degree_high'] = 3.0
        quantiles['out_degree_low'] = 1.0
    
    logger.debug(f"Computed quantiles: {quantiles}")
    
    # Compute binder properties if observer and deltas available
    binder_properties = {}
    if continuation_observer is not None and edge_deltas is not None:
        for cluster_id, cluster_identities in clusters.items():
            binder_props = compute_binder_properties(
                cluster_identities, identity_vectors, continuation_observer, edge_deltas
            )
            binder_properties[cluster_id] = binder_props
    
    # Collect binder metrics for quantiles
    all_betweenness = []
    all_delta_variance = []
    all_bridge_frequency = []
    if binder_properties:
        for props in binder_properties.values():
            all_betweenness.append(props['betweenness_like'])
            all_delta_variance.append(props['edge_delta_variance'])
            all_bridge_frequency.append(props['bridge_frequency'])
    
    if all_betweenness:
        quantiles['betweenness_high'] = calculate_percentile(all_betweenness, percentile_high)
    else:
        quantiles['betweenness_high'] = 2.0
    
    if all_delta_variance:
        quantiles['delta_variance_high'] = calculate_percentile(all_delta_variance, percentile_high)
    else:
        quantiles['delta_variance_high'] = 0.1

    if all_bridge_frequency:
        quantiles['bridge_frequency_high'] = calculate_percentile(all_bridge_frequency, percentile_high)
    else:
        quantiles['bridge_frequency_high'] = 0.5
    
    # Assign roles
    roles = {}
    
    for cluster_id, props in cluster_properties.items():
        if not props:
            roles[cluster_id] = 'unclassified'
            continue
        
        # Determine role from properties (functional, not POS)
        role = None
        
        # Anchor: high survival, low entropy, high concentration
        if (props['avg_survival'] > quantiles['survival_high'] and
            props['avg_entropy'] < quantiles['entropy_low'] and
            props['avg_concentration'] > quantiles['concentration_high']):
            role = 'anchor'
        
        # Driver: high k_reach, high out_degree
        elif (props['avg_k_reach'] > quantiles['k_reach_high'] and
              props['avg_out_degree'] > quantiles['out_degree_high']):
            role = 'driver'
        
        # Gate: low out_degree, high refusal_rate
        elif (props['avg_out_degree'] < quantiles['out_degree_low'] and
              props['avg_refusal_rate'] > quantiles['refusal_high']):
            role = 'gate'
        
        # Terminator: low survival, high refusal_rate
        elif (props['avg_survival'] < quantiles['survival_low'] and
              props['avg_refusal_rate'] > quantiles['refusal_high']):
            role = 'terminator'
        
        # Binder: derived from topology (CORRECTED)
        elif (cluster_id in binder_properties and
              binder_properties[cluster_id]['betweenness_like'] > quantiles['betweenness_high'] and
              binder_properties[cluster_id]['edge_delta_variance'] > quantiles['delta_variance_high'] and
              binder_properties[cluster_id]['bridge_frequency'] > quantiles['bridge_frequency_high']):
            role = 'binder'
        
        # Unclassified (not default binder)
        if role is None:
            role = 'unclassified'
        
        roles[cluster_id] = role
    
    # ORDINAL FALLBACK: When all clusters are unclassified or too few clusters,
    # use ordinal ranking on a single axis to guarantee role diversity.
    # This is first-principles (ordinal, not hand thresholds).
    unclassified_count = sum(1 for r in roles.values() if r == 'unclassified')
    num_clusters = len(clusters)
    
    # Apply fallback if: (1) all unclassified, or (2) only 2 clusters and both unclassified
    if (unclassified_count == num_clusters) or (num_clusters == 2 and unclassified_count == 2):
        logger.info(
            f"Applying ordinal fallback: {unclassified_count}/{num_clusters} unclassified, "
            f"using survival-based ranking"
        )
        
        # Sort clusters by avg_survival (descending)
        # This is ordinal ranking, not threshold-based
        cluster_survivals = [
            (cluster_id, cluster_properties[cluster_id].get('avg_survival', 0.0))
            for cluster_id in clusters.keys()
        ]
        cluster_survivals.sort(key=lambda x: x[1], reverse=True)
        
        # Assign roles based on ordinal position
        for idx, (cluster_id, _) in enumerate(cluster_survivals):
            if idx == 0:
                # Top cluster: highest survival → anchor_candidate
                roles[cluster_id] = 'anchor_candidate'
            elif idx == len(cluster_survivals) - 1:
                # Bottom cluster: lowest survival → terminator_candidate
                roles[cluster_id] = 'terminator_candidate'
            else:
                # Middle clusters: intermediate → driver_candidate
                roles[cluster_id] = 'driver_candidate'
        
        logger.info(
            f"Ordinal fallback applied: {dict(roles)} "
            f"(ranked by survival: {[f'{c}={s:.3f}' for c, s in cluster_survivals]})"
        )
    
    logger.info(f"Final assigned roles: {dict(roles)}")
    
    return roles
