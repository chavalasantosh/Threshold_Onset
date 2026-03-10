"""
THRESHOLD_ONSET — Phase 2: PERSISTENCE

Persistence measurement without naming.
Tracks how long segments persist across iterations.
Returns counts only. No names, no labels, no interpretation.

CONSTRAINT: Thresholds must be FIXED, EXTERNAL, and NON-ADAPTIVE.
No learning, tuning, or optimization allowed.
"""

import hashlib

# FIXED threshold for persistence detection (non-adaptive)
# This value is external and fixed, not computed from data
PERSISTENCE_THRESHOLD = 2


def measure_persistence(residue_sequences, threshold=PERSISTENCE_THRESHOLD):
    """
    Measure persistence of segments across multiple Phase 0 iterations.
    
    Tracks segments that appear in multiple iterations.
    Uses EXACT EQUALITY for segment comparison.
    
    Args:
        residue_sequences: list of residue sequences (each from a Phase 0 iteration)
        threshold: fixed persistence threshold (default: PERSISTENCE_THRESHOLD)
    
    Returns:
        Dictionary with:
        - 'persistence_counts': dict mapping segment hash to persistence count (int)
        - 'persistent_segment_hashes': list of hashes for segments that persist above threshold
    """
    if len(residue_sequences) < 2:
        return {
            'persistence_counts': {},
            'persistent_segment_hashes': []
        }
    
    # Track segments across iterations using EXACT EQUALITY
    segment_counts = {}
    
    # Use fixed window size for segment definition
    SEGMENT_WINDOW = 2
    
    for sequence in residue_sequences:
        # Extract all segments of fixed window size
        seen_in_this_iteration = set()
        
        for i in range(len(sequence) - SEGMENT_WINDOW + 1):
            segment = tuple(sequence[i:i + SEGMENT_WINDOW])
            # Generate internal hash for segment (mechanical identifier only)
            segment_hash = _hash_segment(segment)
            
            # Count persistence (only once per iteration)
            if segment_hash not in seen_in_this_iteration:
                segment_counts[segment_hash] = segment_counts.get(segment_hash, 0) + 1
                seen_in_this_iteration.add(segment_hash)
    
    # Identify segments that persist above threshold
    persistent_hashes = [
        seg_hash for seg_hash, count in segment_counts.items()
        if count >= threshold
    ]
    
    return {
        'persistence_counts': segment_counts,
        'persistent_segment_hashes': persistent_hashes
    }


def _hash_segment(segment):
    """
    Generate internal identity hash for a segment.
    
    Hash is for internal tracking only, not a name or symbol.
    
    Args:
        segment: tuple of residues (fixed window)
    
    Returns:
        Hash value (internal identifier only)
    """
    # Convert segment to bytes for hashing
    segment_bytes = str(segment).encode('utf-8')
    return hashlib.md5(segment_bytes).hexdigest()
