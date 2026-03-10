"""
THRESHOLD_ONSET — Phase 2: REPEATABLE

Repeatable unit detection without naming.
Identifies segments that repeat across different contexts.
Returns counts only. No unit names, no labels, no interpretation.

CONSTRAINT: Uses EXACT EQUALITY only.
No approximate matching or abstraction allowed.
"""

import hashlib

# FIXED threshold for repeatability detection (non-adaptive)
# This value is external and fixed, not computed from data
REPEATABILITY_THRESHOLD = 2


def detect_repeatable_units(residues, threshold=REPEATABILITY_THRESHOLD):
    """
    Detect units that repeat consistently across different contexts.
    
    Uses EXACT EQUALITY for unit comparison.
    No abstraction or compression.
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
        threshold: fixed repeatability threshold (default: REPEATABILITY_THRESHOLD)
    
    Returns:
        Dictionary with:
        - 'repeatability_counts': dict mapping unit hash to repeat count (int)
        - 'repeatable_unit_hashes': list of hashes for units that repeat above threshold
    """
    if len(residues) < 2:
        return {
            'repeatability_counts': {},
            'repeatable_unit_hashes': []
        }
    
    # Fixed window size for unit definition
    UNIT_WINDOW = 2
    
    # Track all units and their repeat counts
    unit_counts = {}
    
    # Extract all units of fixed window size
    for i in range(len(residues) - UNIT_WINDOW + 1):
        unit = tuple(residues[i:i + UNIT_WINDOW])
        # Generate internal hash for unit (mechanical identifier only)
        unit_hash = _hash_unit(unit)
        
        # Count occurrences using EXACT EQUALITY
        unit_counts[unit_hash] = unit_counts.get(unit_hash, 0) + 1
    
    # Identify units that repeat above threshold
    repeatable_hashes = [
        unit_hash for unit_hash, count in unit_counts.items()
        if count >= threshold
    ]
    
    return {
        'repeatability_counts': unit_counts,
        'repeatable_unit_hashes': repeatable_hashes
    }


def _hash_unit(unit):
    """
    Generate internal identity hash for a unit.
    
    Hash is for internal tracking only, not a name or symbol.
    
    Args:
        unit: tuple of residues (fixed window)
    
    Returns:
        Hash value (internal identifier only)
    """
    # Convert unit to bytes for hashing
    unit_bytes = str(unit).encode('utf-8')
    return hashlib.md5(unit_bytes).hexdigest()
