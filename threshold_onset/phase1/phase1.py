"""
THRESHOLD_ONSET — Phase 1: SEGMENTATION

Segmentation without naming.
Boundary detection, clustering, pattern detection.
Returns structural metrics only. No interpretation.

Phase 1 operates as separate layer from Phase 0.
Reads Phase 0 output only. Does not modify Phase 0.
"""


def phase1(residues):
    """
    Phase 1 segmentation pipeline.
    
    Operates on opaque residues from Phase 0.
    Performs segmentation without naming.
    Returns structural metrics only (numbers/indices).
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
    
    Returns:
        Dictionary with structural metrics:
        - 'boundary_positions': list of boundary indices
        - 'cluster_count': number of clusters (int)
        - 'cluster_sizes': list of cluster sizes (unordered)
        - 'distances': list of pairwise distances (raw numbers)
        - 'repetition_count': number of exact repetitions (int)
        - 'survival_count': number of surviving sequences (int)
    """
    from threshold_onset.phase1.boundary import detect_boundaries  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase1.cluster import cluster_residues  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase1.distance import pairwise_distances  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase1.pattern import detect_repetition  # pylint: disable=import-outside-toplevel
    
    # Boundary detection
    boundary_positions = detect_boundaries(residues)
    
    # Clustering
    cluster_result = cluster_residues(residues)
    
    # Distance measurement
    distances = pairwise_distances(residues)
    
    # Pattern detection
    pattern_result = detect_repetition(residues)
    
    return {
        'boundary_positions': boundary_positions,
        'cluster_count': cluster_result['cluster_count'],
        'cluster_sizes': cluster_result['cluster_sizes'],
        'distances': distances,
        'repetition_count': pattern_result['repetition_count'],
        'survival_count': 0  # Requires multiple sequences, handled separately if needed
    }
