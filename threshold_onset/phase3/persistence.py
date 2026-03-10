"""
THRESHOLD_ONSET — Phase 3: RELATION

Relation persistence measurement without naming.
Measures which relations persist across multiple runs.

CONSTRAINT: Uses EXACT EQUALITY only.
Fixed threshold (non-adaptive).
"""

# FIXED threshold for relation persistence (non-adaptive)
# This value is external and fixed, not computed from data
RELATION_PERSISTENCE_THRESHOLD = 2


def measure_relation_persistence(relation_hashes_per_run, threshold=RELATION_PERSISTENCE_THRESHOLD):
    """
    Measure which relations persist across multiple runs.
    
    A relation is persistent if it appears in ≥ threshold runs.
    Uses EXACT EQUALITY for relation_hash comparison.
    
    Args:
        relation_hashes_per_run: list of sets (one set per run)
            Each set contains relation_hashes from that run
        threshold: fixed persistence threshold (default: RELATION_PERSISTENCE_THRESHOLD)
    
    Returns:
        Dictionary with:
        - 'persistence_counts': dict mapping relation_hash to persistence count (int)
        - 'persistent_relation_hashes': set of persistent relation hashes
        - 'persistence_rate': float (0.0 to 1.0) - ratio of persistent relations
    """
    if len(relation_hashes_per_run) < threshold:
        return {
            'persistence_counts': {},
            'persistent_relation_hashes': set(),
            'persistence_rate': 0.0
        }
    
    # Aggregate all unique relation_hashes across all runs
    aggregated_relation_hashes = set()
    for relation_set in relation_hashes_per_run:
        aggregated_relation_hashes.update(relation_set)
    
    # Count how many runs contain each relation_hash
    persistence_counts = {}
    
    for relation_hash in aggregated_relation_hashes:
        # Count runs containing this relation_hash
        run_count = 0
        for relation_set in relation_hashes_per_run:
            # Use exact equality for hash comparison
            if relation_hash in relation_set:
                run_count += 1
        
        persistence_counts[relation_hash] = run_count
    
    # Identify persistent relations (appearing in ≥ threshold runs)
    persistent_relation_hashes = {
        relation_hash for relation_hash, count in persistence_counts.items()
        if count >= threshold
    }
    
    # Compute persistence rate
    total_relations = len(aggregated_relation_hashes)
    persistent_relations = len(persistent_relation_hashes)
    persistence_rate = persistent_relations / total_relations if total_relations > 0 else 0.0
    
    return {
        'persistence_counts': persistence_counts,
        'persistent_relation_hashes': persistent_relation_hashes,
        'persistence_rate': persistence_rate
    }
