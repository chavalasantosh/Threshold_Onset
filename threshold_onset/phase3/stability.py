"""
THRESHOLD_ONSET — Phase 3: RELATION

Relation stability measurement without naming.
Measures numerical stability of relations across runs.

CONSTRAINT: Stability is SECONDARY to persistence.
Only measures stability on persistent relations, not transient relations.
Uses EXACT EQUALITY only.
Fixed thresholds (non-adaptive).
"""

# FIXED thresholds for stability measurement (non-adaptive)
# These values are external and fixed, not computed from data
# NOTE: Variance threshold applies to normalized frequency variance (0.0 to 1.0 range)
# This measures structural consistency, not absolute magnitude
# Normalized frequencies are in [0.0, 1.0], so variance threshold must be much smaller
STABILITY_VARIANCE_THRESHOLD = 0.01  # Normalized frequency variance threshold (structural consistency)
STABILITY_RATIO_THRESHOLD = 0.6


def measure_relation_stability(relation_hashes_per_run, relation_counts_per_run, graph_metrics_per_run, persistent_relation_hashes):
    """
    Measure numerical stability of relations across runs.
    
    CRITICAL: Stability is secondary to persistence.
    Only measures stability on persistent_relation_hashes, not transient relations.
    
    Stability metrics:
    1. Frequency stability: variance of occurrence counts for persistent relations
    2. Edge density stability: variance of edge_count / node_count across runs
    3. Graph structure stability: ratio of common edges across runs
    
    Args:
        relation_hashes_per_run: list of sets (one set per run)
        relation_counts_per_run: list of dicts (one dict per run, mapping relation_hash to count)
        graph_metrics_per_run: list of dicts (one dict per run with 'node_count' and 'edge_count')
        persistent_relation_hashes: set of persistent relation hashes (already filtered)
    
    Returns:
        Dictionary with:
        - 'stability_counts': dict mapping relation_hash to stability count (int)
        - 'stable_relation_hashes': set of stable relation hashes
        - 'stability_ratio': float (0.0 to 1.0) - ratio of stable relations
        - 'edge_density_variance': float - variance of edge density across runs
        - 'common_edges_ratio': float (0.0 to 1.0) - ratio of common edges across runs
    """
    if len(relation_hashes_per_run) < 2:
        return {
            'stability_counts': {},
            'stable_relation_hashes': set(),
            'stability_ratio': 0.0,
            'edge_density_variance': 0.0,
            'common_edges_ratio': 0.0
        }
    
    # 1. Frequency Stability: Measure variance of normalized frequencies for persistent relations
    # CRITICAL: Normalize by total relations per run to measure structural consistency, not absolute magnitude
    # This is still numeric and structural - no meaning added
    stability_counts = {}
    stable_relation_hashes = set()
    
    # Compute total relations per run for normalization
    total_relations_per_run = []
    for relation_counts in relation_counts_per_run:
        total_relations = sum(relation_counts.values()) if relation_counts else 1
        total_relations_per_run.append(total_relations)
    
    for relation_hash in persistent_relation_hashes:
        # Collect normalized frequencies for this relation_hash across all runs
        normalized_frequencies = []
        for idx, relation_counts in enumerate(relation_counts_per_run):
            count = relation_counts.get(relation_hash, 0)
            total_relations = total_relations_per_run[idx]
            # Normalize: frequency = count / total_relations (structural ratio, not meaning)
            normalized_freq = count / total_relations if total_relations > 0 else 0.0
            normalized_frequencies.append(normalized_freq)
        
        # Compute variance of normalized frequencies
        if len(normalized_frequencies) > 1:
            mean_freq = sum(normalized_frequencies) / len(normalized_frequencies)
            variance = sum((freq - mean_freq) ** 2 for freq in normalized_frequencies) / len(normalized_frequencies)
            
            # Mark as stable if variance ≤ threshold
            # Threshold applies to normalized frequency variance (structural consistency)
            if variance <= STABILITY_VARIANCE_THRESHOLD:
                stability_counts[relation_hash] = len(normalized_frequencies)
                stable_relation_hashes.add(relation_hash)
    
    # Compute stability ratio
    persistent_count = len(persistent_relation_hashes)
    stable_count = len(stable_relation_hashes)
    stability_ratio = stable_count / persistent_count if persistent_count > 0 else 0.0
    
    # 2. Edge Density Stability: Compute variance of edge_count / node_count across runs
    edge_densities = []
    for graph_metrics in graph_metrics_per_run:
        node_count = graph_metrics.get('node_count', 1)  # Avoid division by zero
        edge_count = graph_metrics.get('edge_count', 0)
        density = edge_count / node_count if node_count > 0 else 0.0
        edge_densities.append(density)
    
    if len(edge_densities) > 1:
        mean_density = sum(edge_densities) / len(edge_densities)
        edge_density_variance = sum((density - mean_density) ** 2 for density in edge_densities) / len(edge_densities)
    else:
        edge_density_variance = 0.0
    
    # 3. Graph Structure Stability: Compute ratio of common edges across runs
    # Extract graph_edges from each run
    graph_edges_per_run = []
    for graph_metrics in graph_metrics_per_run:
        edges = graph_metrics.get('graph_edges', set())
        graph_edges_per_run.append(edges)
    
    # Compute intersection of all edge sets (common edges)
    if len(graph_edges_per_run) > 0:
        common_edges = graph_edges_per_run[0].copy()
        for edges in graph_edges_per_run[1:]:
            # Use exact equality for edge comparison
            common_edges = common_edges.intersection(edges)
        
        # Compute union of all edge sets (total edges)
        total_edges = set()
        for edges in graph_edges_per_run:
            total_edges.update(edges)
        
        # Common edges ratio
        common_edges_ratio = len(common_edges) / len(total_edges) if len(total_edges) > 0 else 0.0
    else:
        common_edges_ratio = 0.0
    
    return {
        'stability_counts': stability_counts,
        'stable_relation_hashes': stable_relation_hashes,
        'stability_ratio': stability_ratio,
        'edge_density_variance': edge_density_variance,
        'common_edges_ratio': common_edges_ratio
    }
