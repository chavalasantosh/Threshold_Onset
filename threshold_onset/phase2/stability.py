"""
THRESHOLD_ONSET — Phase 2: STABILITY

Stability metrics without naming.
Measures cluster stability across iterations.
Returns counts only. No cluster names, no labels, no interpretation.

CONSTRAINT: Uses EXACT EQUALITY only.
No approximate matching or abstraction allowed.
"""

import hashlib

# FIXED threshold for stability detection (non-adaptive)
# This value is external and fixed, not computed from data
STABILITY_THRESHOLD = 2


def measure_stability(cluster_sequences, threshold=STABILITY_THRESHOLD):
    """
    Measure stability of clusters across iterations.
    
    Tracks which clusters persist across different iterations.
    Uses EXACT EQUALITY for cluster comparison.
    
    Args:
        cluster_sequences: list of cluster sequences (each is a list of clusters from Phase 1)
                          Each cluster is a list of residues
        threshold: fixed stability threshold (default: STABILITY_THRESHOLD)
    
    Returns:
        Dictionary with:
        - 'stability_counts': dict mapping cluster hash to stability count (int)
        - 'stable_cluster_hashes': list of hashes for clusters that are stable above threshold
    """
    if len(cluster_sequences) < 2:
        return {
            'stability_counts': {},
            'stable_cluster_hashes': []
        }
    
    # Track clusters across iterations using EXACT EQUALITY
    cluster_counts = {}
    
    for cluster_sequence in cluster_sequences:
        # Extract clusters from this iteration
        seen_in_this_iteration = set()
        
        for cluster in cluster_sequence:
            # Normalize cluster for comparison (sort residues for exact equality)
            normalized_cluster = tuple(sorted(cluster))
            # Generate internal hash for cluster (mechanical identifier only)
            cluster_hash = _hash_cluster(normalized_cluster)
            
            # Count stability (only once per iteration)
            if cluster_hash not in seen_in_this_iteration:
                cluster_counts[cluster_hash] = cluster_counts.get(cluster_hash, 0) + 1
                seen_in_this_iteration.add(cluster_hash)
    
    # Identify clusters that are stable above threshold
    stable_hashes = [
        cluster_hash for cluster_hash, count in cluster_counts.items()
        if count >= threshold
    ]
    
    return {
        'stability_counts': cluster_counts,
        'stable_cluster_hashes': stable_hashes
    }


def _hash_cluster(cluster):
    """
    Generate internal identity hash for a cluster.
    
    Hash is for internal tracking only, not a name or symbol.
    
    Args:
        cluster: tuple of sorted residues (normalized cluster)
    
    Returns:
        Hash value (internal identifier only)
    """
    # Convert cluster to bytes for hashing
    cluster_bytes = str(cluster).encode('utf-8')
    return hashlib.md5(cluster_bytes).hexdigest()
