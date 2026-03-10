"""
THRESHOLD_ONSET — Phase 3: RELATION

Interaction detection without naming.
Detects when identity hashes appear together (co-occurrence patterns).

CONSTRAINT: Only EXACT EQUALITY allowed.
Hash pairs only (no names, no labels).
Fixed window size (non-adaptive).
"""

import hashlib

# FIXED thresholds for interaction detection (non-adaptive)
# These values are external and fixed, not computed from data
INTERACTION_THRESHOLD = 1
INTERACTION_WINDOW = 3


def detect_interactions(residues, phase2_metrics, threshold=INTERACTION_THRESHOLD, window=INTERACTION_WINDOW):
    """
    Detect when identity hashes appear together (co-occurrence patterns).
    
    Uses EXACT EQUALITY for hash comparison.
    Scans residues with fixed window to detect co-occurrence.
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
        phase2_metrics: dictionary with Phase 2 identity metrics
        threshold: fixed interaction threshold (default: INTERACTION_THRESHOLD)
        window: fixed window size for co-occurrence detection (default: INTERACTION_WINDOW)
    
    Returns:
        Dictionary with:
        - 'interaction_counts': dict mapping (hash1, hash2) tuple to interaction count (int)
        - 'interaction_pairs': set of hash pair tuples (internal identifiers only)
    """
    if len(residues) < window:
        return {
            'interaction_counts': {},
            'interaction_pairs': set()
        }
    
    # Map residues to identity hashes
    # Use same segment window as Phase 2 (SEGMENT_WINDOW = 2)
    SEGMENT_WINDOW = 2
    residue_to_identity = _map_residues_to_identities(residues, phase2_metrics, SEGMENT_WINDOW)
    
    # Track interaction counts
    interaction_counts = {}
    
    # Scan residues with fixed window
    for i in range(len(residues) - window + 1):
        window_residues = residues[i:i + window]
        
        # Get identity hashes for residues in this window
        window_identities = set()
        for residue_idx in range(i, i + window):
            if residue_idx in residue_to_identity:
                identity_hashes = residue_to_identity[residue_idx]
                window_identities.update(identity_hashes)
        
        # Create interaction pairs from identities in same window
        identity_list = list(window_identities)
        for j, hash1 in enumerate(identity_list):
            for hash2 in identity_list[j+1:]:
                # Use exact equality for hash comparison
                if hash1 != hash2:
                    # Use canonical ordering (smaller hash first)
                    if hash1 < hash2:
                        pair = (hash1, hash2)
                    else:
                        pair = (hash2, hash1)
                    
                    # Count interaction using EXACT EQUALITY
                    interaction_counts[pair] = interaction_counts.get(pair, 0) + 1
    
    # Identify interaction pairs above threshold
    interaction_pairs = {
        pair for pair, count in interaction_counts.items()
        if count >= threshold
    }
    
    return {
        'interaction_counts': interaction_counts,
        'interaction_pairs': interaction_pairs
    }


def _map_residues_to_identities(residues, phase2_metrics, segment_window):
    """
    Map residue indices to identity hashes.
    
    Creates segments from residues, hashes them, and looks up in identity_mappings.
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
        phase2_metrics: dictionary with Phase 2 identity metrics
        segment_window: fixed window size for segment creation
    
    Returns:
        Dictionary mapping residue index to set of identity hashes
    """
    residue_to_identity = {}
    
    if 'identity_mappings' not in phase2_metrics:
        return residue_to_identity
    
    identity_mappings = phase2_metrics['identity_mappings']
    
    # Create segments and map to identity hashes
    for i in range(len(residues) - segment_window + 1):
        segment = tuple(residues[i:i + segment_window])
        segment_hash = _hash_segment(segment)
        
        # Look up identity hash in identity_mappings
        if segment_hash in identity_mappings:
            identity_hash = identity_mappings[segment_hash]
            
            # Map all residue indices in this segment to the identity hash
            for residue_idx in range(i, i + segment_window):
                if residue_idx not in residue_to_identity:
                    residue_to_identity[residue_idx] = set()
                residue_to_identity[residue_idx].add(identity_hash)
    
    # Also map from repeatable_unit_hashes
    if 'repeatable_unit_hashes' in phase2_metrics:
        repeatable_hashes = phase2_metrics['repeatable_unit_hashes']
        
        for i in range(len(residues) - segment_window + 1):
            unit = tuple(residues[i:i + segment_window])
            unit_hash = _hash_segment(unit)
            
            if unit_hash in repeatable_hashes:
                for residue_idx in range(i, i + segment_window):
                    if residue_idx not in residue_to_identity:
                        residue_to_identity[residue_idx] = set()
                    residue_to_identity[residue_idx].add(unit_hash)
    
    return residue_to_identity


def _hash_segment(segment):
    """
    Generate hash for a segment (internal tracking only).
    
    Uses same hashing method as Phase 2 for consistency.
    
    Args:
        segment: tuple of residues (fixed window)
    
    Returns:
        Hash value (internal identifier only)
    """
    segment_bytes = str(segment).encode('utf-8')
    return hashlib.md5(segment_bytes).hexdigest()
