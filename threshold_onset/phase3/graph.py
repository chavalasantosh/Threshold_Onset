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
    
    # Create edges based on co-occurrence in identity_mappings
    # If two segment hashes map to different identity hashes, create edge
    edges = set()
    
    if 'identity_mappings' in phase2_metrics:
        identity_mappings = phase2_metrics['identity_mappings']
        identity_hashes = list(identity_mappings.values())
        
        # Create edges between identity hashes that co-occur
        # (appear in the same mapping context)
        for i, hash1 in enumerate(identity_hashes):
            for hash2 in identity_hashes[i+1:]:
                # Use exact equality for hash comparison
                if hash1 != hash2:
                    # Create undirected edge (both directions)
                    edge1 = (hash1, hash2)
                    edge2 = (hash2, hash1)
                    # Use canonical ordering (smaller hash first) to avoid duplicates
                    if hash1 < hash2:
                        edges.add((hash1, hash2))
                    else:
                        edges.add((hash2, hash1))
    
    # Also create edges from persistent segments that share identity hashes
    # This captures relationships between different identity types
    if 'persistent_segment_hashes' in phase2_metrics and 'identity_mappings' in phase2_metrics:
        persistent_hashes = phase2_metrics['persistent_segment_hashes']
        identity_mappings = phase2_metrics['identity_mappings']
        
        # Map persistent segments to their identity hashes
        persistent_to_identity = {}
        for seg_hash in persistent_hashes:
            if seg_hash in identity_mappings:
                identity_hash = identity_mappings[seg_hash]
                if identity_hash not in persistent_to_identity:
                    persistent_to_identity[identity_hash] = []
                persistent_to_identity[identity_hash].append(seg_hash)
        
        # Create edges between identity hashes that share persistent segments
        identity_list = list(persistent_to_identity.keys())
        for i, hash1 in enumerate(identity_list):
            for hash2 in identity_list[i+1:]:
                # Use exact equality for hash comparison
                if hash1 != hash2:
                    # Use canonical ordering
                    if hash1 < hash2:
                        edges.add((hash1, hash2))
                    else:
                        edges.add((hash2, hash1))
    
    return {
        'nodes': nodes,
        'edges': edges
    }
