"""
THRESHOLD_ONSET — Phase 3: RELATION

Relation persistence measurement without naming.
Measures which relations persist across multiple runs.

CONSTRAINT: Uses EXACT EQUALITY only.
Fixed threshold (non-adaptive).
"""

from collections import Counter

# FIXED threshold for relation persistence (non-adaptive)
# This value is external and fixed, not computed from data
RELATION_PERSISTENCE_THRESHOLD = 2


def measure_relation_persistence(relation_hashes_per_run, threshold=RELATION_PERSISTENCE_THRESHOLD):
    """
    Measure which relations persist across multiple runs.

    A relation is persistent if it appears in >= threshold runs.
    Uses EXACT EQUALITY for relation_hash comparison.

    O(R × U) single-pass using Counter.update() — was O(U × R) nested loop.

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

    # Single-pass: each run's set contributes +1 to each hash it contains.
    # Counter.update() on a set is O(set_size) with no nested per-hash scan.
    persistence_counts: Counter = Counter()
    for relation_set in relation_hashes_per_run:
        persistence_counts.update(relation_set)

    # Identify persistent relations (appearing in >= threshold runs)
    persistent_relation_hashes = {
        h for h, count in persistence_counts.items() if count >= threshold
    }

    total_relations = len(persistence_counts)
    persistence_rate = (
        len(persistent_relation_hashes) / total_relations if total_relations > 0 else 0.0
    )

    return {
        'persistence_counts': dict(persistence_counts),
        'persistent_relation_hashes': persistent_relation_hashes,
        'persistence_rate': persistence_rate
    }
