"""
THRESHOLD_ONSET — Phase 3: RELATION

Relation hash generation without naming.
Generates structural relation signatures (hash-only, no names).

CONSTRAINT: Relation type hashes must be FIXED and GLOBAL.
Computed once at module level, not derived dynamically.
"""

import hashlib

# FIXED relation type hashes (computed once at module level)
# CRITICAL: These must be global and fixed, not derived dynamically
# This avoids "relation drift" and ensures consistency across runs
INTERACTION_TYPE_HASH = hashlib.sha256(b"interaction").hexdigest()
DEPENDENCY_TYPE_HASH = hashlib.sha256(b"dependency").hexdigest()
INFLUENCE_TYPE_HASH = hashlib.sha256(b"influence").hexdigest()


def generate_relation_hash(source_hash, target_hash, relation_type_hash):
    """
    Generate hash-based relation identifier.
    
    Creates a structural relation signature from source, target, and type.
    All components are hashes (internal identifiers only).
    
    Args:
        source_hash: Identity hash of source (from Phase 2)
        target_hash: Identity hash of target (from Phase 2)
        relation_type_hash: Hash identifying relation type (fixed constant)
    
    Returns:
        Relation hash (string, internal identifier only)
    """
    # Combine components for hashing
    # Use canonical ordering: source < target for consistency
    if source_hash < target_hash:
        relation_input = f"{source_hash}:{target_hash}:{relation_type_hash}".encode('utf-8')
    else:
        relation_input = f"{target_hash}:{source_hash}:{relation_type_hash}".encode('utf-8')
    
    # Generate relation hash using SHA256
    relation_hash = hashlib.sha256(relation_input).hexdigest()
    
    return relation_hash


def extract_relations(phase3_metrics):
    """
    Extract all relations from Phase 3 metrics and generate relation_hashes.
    
    Processes interaction_pairs, dependency_pairs, and influence_counts
    to generate relation_hashes for each relation type.
    
    Args:
        phase3_metrics: dictionary with Phase 3 relation metrics
    
    Returns:
        Dictionary with:
        - 'relation_hashes': set of relation hashes (internal identifiers only)
        - 'relation_counts': dict mapping relation_hash to occurrence count (int)
    """
    relation_hashes = set()
    relation_counts = {}
    
    # Extract interaction relations
    if 'interaction_pairs' in phase3_metrics:
        for source_hash, target_hash in phase3_metrics['interaction_pairs']:
            relation_hash = generate_relation_hash(source_hash, target_hash, INTERACTION_TYPE_HASH)
            relation_hashes.add(relation_hash)
            
            # Count occurrences from interaction_counts
            pair = (source_hash, target_hash) if source_hash < target_hash else (target_hash, source_hash)
            if pair in phase3_metrics.get('interaction_counts', {}):
                count = phase3_metrics['interaction_counts'][pair]
                relation_counts[relation_hash] = relation_counts.get(relation_hash, 0) + count
    
    # Extract dependency relations
    if 'dependency_pairs' in phase3_metrics:
        for source_hash, target_hash in phase3_metrics['dependency_pairs']:
            relation_hash = generate_relation_hash(source_hash, target_hash, DEPENDENCY_TYPE_HASH)
            relation_hashes.add(relation_hash)
            
            # Count occurrences from dependency_counts
            pair = (source_hash, target_hash) if source_hash < target_hash else (target_hash, source_hash)
            if pair in phase3_metrics.get('dependency_counts', {}):
                count = phase3_metrics['dependency_counts'][pair]
                relation_counts[relation_hash] = relation_counts.get(relation_hash, 0) + count
    
    # Extract influence relations
    if 'influence_counts' in phase3_metrics:
        for (source_hash, target_hash), count in phase3_metrics['influence_counts'].items():
            relation_hash = generate_relation_hash(source_hash, target_hash, INFLUENCE_TYPE_HASH)
            relation_hashes.add(relation_hash)
            relation_counts[relation_hash] = relation_counts.get(relation_hash, 0) + count
    
    return {
        'relation_hashes': relation_hashes,
        'relation_counts': relation_counts
    }
