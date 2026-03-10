"""
THRESHOLD_ONSET — Phase 1: BOUNDARY

Boundary detection without naming.
Detects separation points where residues differ.
Returns indices only. No labels, no interpretation.

CONSTRAINT: Thresholds must be FIXED, EXTERNAL, and NON-ADAPTIVE.
No learning, tuning, or optimization allowed.
"""

# FIXED threshold for boundary detection (non-adaptive)
# This value is external and fixed, not computed from data
BOUNDARY_THRESHOLD = 0.1


def detect_boundaries(residues, threshold=BOUNDARY_THRESHOLD):
    """
    Detect boundaries where consecutive residues differ significantly.
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
        threshold: fixed threshold for boundary detection (default: BOUNDARY_THRESHOLD)
    
    Returns:
        List of boundary positions (indices only, no labels, no interpretation)
    """
    if len(residues) < 2:
        return []
    
    from threshold_onset.phase1.distance import absolute_difference  # pylint: disable=import-outside-toplevel
    
    boundaries = []
    for i in range(len(residues) - 1):
        diff = absolute_difference(residues[i], residues[i + 1])
        if diff > threshold:
            boundaries.append(i + 1)  # Position after the boundary
    
    return boundaries
