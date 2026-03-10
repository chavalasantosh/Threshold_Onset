"""
THRESHOLD_ONSET — Phase 3: RELATION

Dependency measurement without naming.
Measures dependencies between identity hashes (which identities depend on others).

CONSTRAINT: Only EXACT EQUALITY allowed.
Hash pairs only (no names, no labels).
Fixed window size (non-adaptive).
Temporal ordering only (no interpretation).
"""

import hashlib

# FIXED thresholds for dependency detection (non-adaptive)
# These values are external and fixed, not computed from data
DEPENDENCY_THRESHOLD = 1
DEPENDENCY_WINDOW = 2


def measure_dependencies(residues, phase2_metrics, threshold=DEPENDENCY_THRESHOLD, window=DEPENDENCY_WINDOW):
    """
    Measure dependencies between identity hashes.
    
    Detects when one identity hash appears before another within fixed window (temporal dependency).
    Uses EXACT EQUALITY for hash comparison.
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
        phase2_metrics: dictionary with Phase 2 identity metrics
        threshold: fixed dependency threshold (default: DEPENDENCY_THRESHOLD)
        window: fixed window size for dependency detection (default: DEPENDENCY_WINDOW)
    
    Returns:
        Dictionary with:
        - 'dependency_counts': dict mapping (hash1, hash2) tuple to dependency count (int)
        - 'dependency_pairs': set of hash pair tuples (internal identifiers only)
    """
    if len(residues) < window:
        return {
            'dependency_counts': {},
            'dependency_pairs': set()
        }
    
    # Map residues to identity hashes
    # Use same segment window as Phase 2 (SEGMENT_WINDOW = 2)
    SEGMENT_WINDOW = 2
    residue_to_identity = _map_residues_to_identities(residues, phase2_metrics, SEGMENT_WINDOW)
    
    # Track dependency counts
    dependency_counts = {}
    
    # Scan residues with fixed window
    for i in range(len(residues) - window + 1):
        window_residues = residues[i:i + window]
        
        # Get identity hashes for residues in this window (in order)
        window_identities = []
        for residue_idx in range(i, i + window):
            if residue_idx in residue_to_identity:
                identity_hashes = residue_to_identity[residue_idx]
                # For each identity hash at this position
                for identity_hash in identity_hashes:
                    window_identities.append((residue_idx - i, identity_hash))
        
        # Create dependency pairs: earlier identity depends on later identity
        # (temporal ordering: if hash1 appears before hash2, hash2 depends on hash1)
        for j, (pos1, hash1) in enumerate(window_identities):
            for (pos2, hash2) in window_identities[j+1:]:
                # Use exact equality for hash comparison
                if hash1 != hash2:
                    # Temporal dependency: hash1 appears before hash2
                    # Use canonical ordering (smaller hash first) for consistency
                    if hash1 < hash2:
                        pair = (hash1, hash2)
                    else:
                        pair = (hash2, hash1)
                    
                    # Count dependency using EXACT EQUALITY
                    dependency_counts[pair] = dependency_counts.get(pair, 0) + 1
    
    # Identify dependency pairs above threshold
    dependency_pairs = {
        pair for pair, count in dependency_counts.items()
        if count >= threshold
    }
    
    return {
        'dependency_counts': dependency_counts,
        'dependency_pairs': dependency_pairs
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
