"""
THRESHOLD_ONSET — Phase 1: CLUSTER

Clustering without naming or labeling.
Groups residues by proximity.
Returns counts only. No group names, no interpretation.

CONSTRAINT: Clustering thresholds must be FIXED and EXTERNAL.
No adaptive clustering or optimization.
"""

# FIXED threshold for clustering (non-adaptive)
# This value is external and fixed, not computed from data
CLUSTER_THRESHOLD = 0.1


def cluster_residues(residues, threshold=CLUSTER_THRESHOLD):
    """
    Group residues by proximity using fixed threshold.
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
        threshold: fixed distance threshold for clustering (default: CLUSTER_THRESHOLD)
    
    Returns:
        Dictionary with:
        - 'cluster_count': number of clusters (int)
        - 'cluster_sizes': list of cluster sizes (unordered, no distribution interpretation)
    """
    if not residues:
        return {'cluster_count': 0, 'cluster_sizes': []}
    
    # Simple clustering: assign each residue to a cluster
    # If distance to existing cluster center <= threshold, join that cluster
    # Otherwise, create new cluster
    clusters = []
    cluster_centers = []
    cluster_sums = []
    cluster_sizes = []
    
    for residue in residues:
        assigned = False
        for idx, center in enumerate(cluster_centers):
            if abs(residue - center) <= threshold:
                clusters[idx].append(residue)
                # Update center as average (mechanical computation, not adaptation)
                cluster_sums[idx] += residue
                cluster_sizes[idx] += 1
                cluster_centers[idx] = cluster_sums[idx] / cluster_sizes[idx]
                assigned = True
                break
        
        if not assigned:
            clusters.append([residue])
            cluster_centers.append(residue)
            cluster_sums.append(residue)
            cluster_sizes.append(1)
    
    cluster_sizes = [len(cluster) for cluster in clusters]
    
    return {
        'cluster_count': len(clusters),
        'cluster_sizes': cluster_sizes  # Unordered list, no distribution interpretation
    }
