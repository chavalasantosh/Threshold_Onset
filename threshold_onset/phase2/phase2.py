"""
THRESHOLD_ONSET — Phase 2: IDENTITY

Identity without naming.
Persistence measurement without meaning.
Repeatable units without symbols.
Identity hashes (internal only, not symbolic).

Phase 2 operates as separate layer from Phase 0 and Phase 1.
Reads Phase 0 and Phase 1 output only. Does not modify them.
"""


def phase2(residues, phase1_metrics):
    """
    Phase 2 identity pipeline.
    
    Operates on opaque residues from Phase 0 and metrics from Phase 1.
    Performs identity detection without naming.
    Returns identity metrics only (hashes and counts).
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
        phase1_metrics: dictionary with Phase 1 structural metrics
    
    Returns:
        Dictionary with identity metrics:
        - 'persistence_counts': dict mapping segment hash to persistence count
        - 'persistent_segment_hashes': list of persistent segment hashes
        - 'repeatability_counts': dict mapping unit hash to repeat count
        - 'repeatable_unit_hashes': list of repeatable unit hashes
        - 'identity_mappings': dict mapping segment hash to identity hash
        - 'identity_persistence': dict mapping identity hash to persistence count
        - 'stability_counts': dict mapping cluster hash to stability count
        - 'stable_cluster_hashes': list of stable cluster hashes
    """
    from threshold_onset.phase2.persistence import measure_persistence  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase2.repeatable import detect_repeatable_units  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase2.identity import assign_identity_hashes  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase2.stability import measure_stability  # pylint: disable=import-outside-toplevel
    
    # For Phase 2, we need multiple iterations to measure persistence
    # Since Phase 0 runs once, we'll treat the single residue sequence as one iteration
    # For multi-iteration analysis, we would need multiple Phase 0 runs
    # For now, we'll work with the single sequence and detect repeatable units within it
    
    # Persistence measurement (requires multiple iterations)
    # For single iteration, persistence is measured within the sequence
    residue_sequences = [residues]  # Single iteration for now
    persistence_result = measure_persistence(residue_sequences)
    
    # Repeatable unit detection (works on single sequence)
    repeatable_result = detect_repeatable_units(residues)
    
    # Identity hash assignment (requires multiple iterations)
    identity_result = assign_identity_hashes(residue_sequences)
    
    # Stability measurement (requires cluster sequences from multiple iterations)
    # For single iteration, we'll construct cluster sequence from Phase 1 metrics
    # Phase 1 provides cluster_count and cluster_sizes, but not actual cluster contents
    # We'll need to reconstruct clusters from residues using Phase 1's clustering logic
    cluster_sequences = _reconstruct_clusters(residues, phase1_metrics)
    stability_result = measure_stability(cluster_sequences)
    
    return {
        'persistence_counts': persistence_result['persistence_counts'],
        'persistent_segment_hashes': persistence_result['persistent_segment_hashes'],
        'repeatability_counts': repeatable_result['repeatability_counts'],
        'repeatable_unit_hashes': repeatable_result['repeatable_unit_hashes'],
        'identity_mappings': identity_result['identity_mappings'],
        'identity_persistence': identity_result['identity_persistence'],
        'stability_counts': stability_result['stability_counts'],
        'stable_cluster_hashes': stability_result['stable_cluster_hashes']
    }


def _reconstruct_clusters(residues, phase1_metrics):
    """
    Reconstruct clusters from residues using Phase 1 clustering logic.
    
    This is necessary because Phase 1 only returns cluster_count and cluster_sizes,
    not the actual cluster contents. We need to reconstruct them for stability measurement.
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
        phase1_metrics: dictionary with Phase 1 structural metrics
    
    Returns:
        List of cluster sequences (single iteration for now)
        Each cluster is a list of residues
    """
    # Import Phase 1 clustering to reconstruct clusters
    from threshold_onset.phase1.cluster import cluster_residues  # pylint: disable=import-outside-toplevel
    
    # Re-cluster using Phase 1 logic (same threshold)
    # This is mechanical reconstruction, not modification of Phase 1
    cluster_result = cluster_residues(residues)
    
    # We need to reconstruct actual cluster contents
    # Since Phase 1 doesn't return cluster contents, we'll use the same clustering logic
    # to get the actual clusters
    from threshold_onset.phase1.distance import absolute_difference  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase1.cluster import CLUSTER_THRESHOLD  # pylint: disable=import-outside-toplevel
    
    clusters = []
    cluster_centers = []
    
    for residue in residues:
        assigned = False
        for idx, center in enumerate(cluster_centers):
            if absolute_difference(residue, center) <= CLUSTER_THRESHOLD:
                clusters[idx].append(residue)
                cluster_centers[idx] = sum(clusters[idx]) / len(clusters[idx])
                assigned = True
                break
        
        if not assigned:
            clusters.append([residue])
            cluster_centers.append(residue)
    
    # Return as sequence of clusters (single iteration)
    return [clusters]


def phase2_multi_run(residue_sequences, phase1_metrics_list):
    """
    Phase 2 identity pipeline with multiple runs.
    
    Tests persistence across multiple independent Phase 0 runs.
    Operates on opaque residues from multiple Phase 0 runs and metrics from Phase 1.
    Performs identity detection without naming.
    Returns identity metrics only (hashes and counts).
    
    Args:
        residue_sequences: list of residue sequences (each from a separate Phase 0 run)
        phase1_metrics_list: list of Phase 1 metrics (one per run)
    
    Returns:
        Dictionary with identity metrics:
        - 'persistence_counts': dict mapping segment hash to persistence count
        - 'persistent_segment_hashes': list of persistent segment hashes
        - 'repeatability_counts': dict mapping unit hash to repeat count
        - 'repeatable_unit_hashes': list of repeatable unit hashes
        - 'identity_mappings': dict mapping segment hash to identity hash
        - 'identity_persistence': dict mapping identity hash to persistence count
        - 'stability_counts': dict mapping cluster hash to stability count
        - 'stable_cluster_hashes': list of stable cluster hashes
    """
    from threshold_onset.phase2.persistence import measure_persistence  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase2.repeatable import detect_repeatable_units  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase2.identity import assign_identity_hashes  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase2.stability import measure_stability  # pylint: disable=import-outside-toplevel
    
    # Persistence measurement across multiple runs
    persistence_result = measure_persistence(residue_sequences)
    
    # Repeatable unit detection (aggregate across all runs)
    # Combine all residues from all runs for repeatability detection
    all_residues = []
    for residues in residue_sequences:
        all_residues.extend(residues)
    repeatable_result = detect_repeatable_units(all_residues)
    
    # Identity hash assignment across multiple runs
    identity_result = assign_identity_hashes(residue_sequences)
    
    # Stability measurement across multiple runs
    # Reconstruct clusters for each run
    cluster_sequences = []
    for residues, phase1_metrics in zip(residue_sequences, phase1_metrics_list):
        clusters = _reconstruct_clusters(residues, phase1_metrics)
        cluster_sequences.extend(clusters)
    stability_result = measure_stability(cluster_sequences)
    
    return {
        'persistence_counts': persistence_result['persistence_counts'],
        'persistent_segment_hashes': persistence_result['persistent_segment_hashes'],
        'repeatability_counts': repeatable_result['repeatability_counts'],
        'repeatable_unit_hashes': repeatable_result['repeatable_unit_hashes'],
        'identity_mappings': identity_result['identity_mappings'],
        'identity_persistence': identity_result['identity_persistence'],
        'stability_counts': stability_result['stability_counts'],
        'stable_cluster_hashes': stability_result['stable_cluster_hashes']
    }