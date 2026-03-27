"""
THRESHOLD_ONSET — Phase 2: IDENTITY

Identity without naming.
Persistence measurement without meaning.
Repeatable units without symbols.
Identity hashes (internal only, not symbolic).

Phase 2 operates as separate layer from Phase 0 and Phase 1.
Reads Phase 0 and Phase 1 output only. Does not modify them.
"""

import os
from concurrent.futures import ThreadPoolExecutor

from threshold_onset.phase2.persistence import measure_persistence
from threshold_onset.phase2.repeatable import detect_repeatable_units
from threshold_onset.phase2.identity import assign_identity_hashes
from threshold_onset.phase2.stability import measure_stability


def _env_int(name, default, minimum=1):
    """Read integer env var safely."""
    raw = os.environ.get(name)
    if not raw:
        return max(minimum, int(default))
    try:
        return max(minimum, int(raw))
    except ValueError:
        return max(minimum, int(default))


def _reconstruct_clusters_task(payload):
    residues, phase1_metrics = payload
    return _reconstruct_clusters(residues, phase1_metrics)


def _derive_virtual_residue_sequences(residues, max_sequences=3):
    """
    Build deterministic sub-sequences from one run so persistence metrics
    can still capture repeat structure in single-run mode.
    """
    if not residues:
        return [[]]
    if len(residues) < 8:
        return [residues]

    window_size = max(8, len(residues) // 2)
    max_start = max(0, len(residues) - window_size)
    if max_start == 0:
        return [residues]

    stride = max(1, max_start // max(1, max_sequences - 1))
    starts = list(range(0, max_start + 1, stride))[:max_sequences]
    sequences = [residues[start:start + window_size] for start in starts]
    return sequences if sequences else [residues]


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
    # Derive deterministic sub-sequences so persistence can be measured
    # from one run without introducing randomness.
    residue_sequences = _derive_virtual_residue_sequences(residues)
    persistence_result = measure_persistence(residue_sequences)
    
    # Repeatable unit detection (works on single sequence)
    repeatable_result = detect_repeatable_units(residues)
    
    # Identity hash assignment (requires multiple iterations)
    identity_result = assign_identity_hashes(residue_sequences)
    
    # Stability measurement requires cluster sequences.
    # In single-run mode, reconstruct from the available residues + Phase 1 metrics.
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

    Reuses cluster_residues(return_members=True) so the algorithm is never
    duplicated — previously the same algorithm was re-implemented here verbatim.

    Args:
        residues: list of opaque residues (floats from Phase 0)
        phase1_metrics: dictionary with Phase 1 structural metrics (unused; kept
                        for API compatibility in case callers pass it)

    Returns:
        List of cluster sequences — each cluster is a list of residues,
        wrapped in an outer list to represent a single-iteration cluster sequence.
    """
    from threshold_onset.phase1.cluster import cluster_residues  # pylint: disable=import-outside-toplevel
    result = cluster_residues(residues, return_members=True)
    return [result.get('cluster_members', [])]


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

    all_residues = []
    for residues in residue_sequences:
        all_residues.extend(residues)

    worker_count = min(
        max(1, _env_int("PHASE2_WORKERS", default=os.cpu_count() or 1)),
        max(1, len(residue_sequences)),
    )

    # Parallelize independent heavy computations.
    if worker_count > 1 and len(residue_sequences) > 1:
        with ThreadPoolExecutor(max_workers=min(worker_count, 3)) as pool:
            f_persistence = pool.submit(measure_persistence, residue_sequences)
            f_repeatable = pool.submit(detect_repeatable_units, all_residues)
            f_identity = pool.submit(assign_identity_hashes, residue_sequences)
            persistence_result = f_persistence.result()
            repeatable_result = f_repeatable.result()
            identity_result = f_identity.result()

        payloads = list(zip(residue_sequences, phase1_metrics_list))
        with ThreadPoolExecutor(max_workers=worker_count) as pool:
            reconstructed = list(pool.map(_reconstruct_clusters_task, payloads))
        cluster_sequences = []
        for clusters in reconstructed:
            cluster_sequences.extend(clusters)
    else:
        # Persistence measurement across multiple runs
        persistence_result = measure_persistence(residue_sequences)
        repeatable_result = detect_repeatable_units(all_residues)
        identity_result = assign_identity_hashes(residue_sequences)

        # Stability measurement across multiple runs
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