"""
THRESHOLD_ONSET — Phase 2: IDENTITY

Identity hash generation without naming.
Generates internal identity hashes for persistent segments.
Hashes are INTERNAL ONLY - not names, not symbols, not labels.

CONSTRAINT: Identity hashes are mechanical identifiers only.
They are NOT to be displayed as names or used as symbols.
"""

import hashlib

# FIXED threshold for identity assignment (non-adaptive)
# This value is external and fixed, not computed from data
IDENTITY_PERSISTENCE_THRESHOLD = 2


def assign_identity_hashes(residue_sequences, threshold=IDENTITY_PERSISTENCE_THRESHOLD):
    """
    Assign internal identity hashes to persistent segments.
    
    Creates identity mappings using hash-based identifiers.
    Hashes are INTERNAL ONLY - not names, not symbols.
    
    Args:
        residue_sequences: list of residue sequences (each from a Phase 0 iteration)
        threshold: fixed persistence threshold for identity assignment (default: IDENTITY_PERSISTENCE_THRESHOLD)
    
    Returns:
        Dictionary with:
        - 'identity_mappings': dict mapping segment hash to identity hash (both are internal identifiers)
        - 'identity_persistence': dict mapping identity hash to persistence count (int)
    """
    if len(residue_sequences) < 2:
        return {
            'identity_mappings': {},
            'identity_persistence': {}
        }
    
    # Fixed window size for segment definition
    SEGMENT_WINDOW = 2
    
    # Track segments and their persistence
    segment_persistence = {}
    
    for sequence in residue_sequences:
        seen_in_this_iteration = set()
        
        for i in range(len(sequence) - SEGMENT_WINDOW + 1):
            segment = tuple(sequence[i:i + SEGMENT_WINDOW])
            segment_hash = _hash_segment(segment)
            
            # Count persistence (only once per iteration)
            if segment_hash not in seen_in_this_iteration:
                segment_persistence[segment_hash] = segment_persistence.get(segment_hash, 0) + 1
                seen_in_this_iteration.add(segment_hash)
    
    # Assign identity hashes only to segments that persist above threshold
    identity_mappings = {}
    identity_persistence = {}
    
    for segment_hash, persistence_count in segment_persistence.items():
        if persistence_count >= threshold:
            # Generate identity hash (internal identifier only, not a name)
            identity_hash = _generate_identity_hash(segment_hash, persistence_count)
            identity_mappings[segment_hash] = identity_hash
            identity_persistence[identity_hash] = persistence_count
    
    return {
        'identity_mappings': identity_mappings,
        'identity_persistence': identity_persistence
    }


def _hash_segment(segment):
    """
    Generate hash for a segment (internal tracking only).
    
    Args:
        segment: tuple of residues (fixed window)
    
    Returns:
        Hash value (internal identifier only)
    """
    segment_bytes = str(segment).encode('utf-8')
    return hashlib.md5(segment_bytes).hexdigest()


def _generate_identity_hash(segment_hash, persistence_count):
    """
    Generate identity hash for a persistent segment.
    
    Identity hash is INTERNAL ONLY - not a name, not a symbol.
    It is a mechanical identifier for tracking purposes only.
    
    Args:
        segment_hash: hash of the segment
        persistence_count: persistence count for the segment
    
    Returns:
        Identity hash value (internal identifier only)
    """
    # Combine segment hash and persistence for identity generation
    identity_input = f"{segment_hash}:{persistence_count}".encode('utf-8')
    return hashlib.sha256(identity_input).hexdigest()
