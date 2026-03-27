"""
THRESHOLD_ONSET — Phase 3: RELATION

Graph structure construction without naming.
Builds graph structures from identity hashes (nodes and edges as hash pairs only).

CONSTRAINT: Graph structures are INTERNAL ONLY.
Nodes are identity hashes (internal identifiers only).
Edges are hash pairs (internal identifiers only).
No node names, no edge labels, no graph visualization.
"""

import hashlib

# FIXED threshold for co-occurrence to create edge (non-adaptive)
# This value is external and fixed, not computed from data
CO_OCCURRENCE_THRESHOLD = 1


def build_graph(phase2_metrics, threshold=CO_OCCURRENCE_THRESHOLD):
    """
    Build graph structure from identity hashes.
    
    Creates nodes from identity hashes and edges from co-occurrence.
    All identifiers are internal only (hashes, not names).
    
    Args:
        phase2_metrics: dictionary with Phase 2 identity metrics
        threshold: fixed co-occurrence threshold (default: CO_OCCURRENCE_THRESHOLD)
    
    Returns:
        Dictionary with:
        - 'nodes': set of identity hashes (internal identifiers only)
        - 'edges': set of hash pair tuples (internal identifiers only)
    """
    # Extract all identity hashes from Phase 2 metrics
    nodes = set()
    
    # Add persistent segment hashes
    if 'persistent_segment_hashes' in phase2_metrics:
        nodes.update(phase2_metrics['persistent_segment_hashes'])
    
    # Add repeatable unit hashes
    if 'repeatable_unit_hashes' in phase2_metrics:
        nodes.update(phase2_metrics['repeatable_unit_hashes'])
    
    # Add stable cluster hashes
    if 'stable_cluster_hashes' in phase2_metrics:
        nodes.update(phase2_metrics['stable_cluster_hashes'])
    
    # Add identity hashes from identity_mappings
    if 'identity_mappings' in phase2_metrics:
        nodes.update(phase2_metrics['identity_mappings'].values())
    
    # Create edges based on co-occurrence in identity_mappings.
    # Use a helper to add a canonical (smaller-first) edge once.
    edges = set()

    def _add_edge(h1, h2):
        if h1 != h2:
            edges.add((h1, h2) if h1 < h2 else (h2, h1))

    if 'identity_mappings' in phase2_metrics:
        identity_hashes = list(phase2_metrics['identity_mappings'].values())
        # Deduplicate first — many segment hashes may map to the same identity hash
        unique_ids = list(dict.fromkeys(identity_hashes))
        for i, hash1 in enumerate(unique_ids):
            for hash2 in unique_ids[i + 1:]:
                _add_edge(hash1, hash2)

    # Also create edges from persistent segments that share identity hashes.
    if 'persistent_segment_hashes' in phase2_metrics and 'identity_mappings' in phase2_metrics:
        identity_mappings = phase2_metrics['identity_mappings']
        seen_ids = set()
        identity_list = []
        for seg_hash in phase2_metrics['persistent_segment_hashes']:
            ih = identity_mappings.get(seg_hash)
            if ih and ih not in seen_ids:
                seen_ids.add(ih)
                identity_list.append(ih)
        for i, hash1 in enumerate(identity_list):
            for hash2 in identity_list[i + 1:]:
                _add_edge(hash1, hash2)

    return {
        'nodes': nodes,
        'edges': edges
    }
