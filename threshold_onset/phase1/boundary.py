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
    
    boundaries = []
    for idx, (left, right) in enumerate(zip(residues, residues[1:])):
        if abs(left - right) > threshold:
            boundaries.append(idx + 1)  # Position after the boundary

    return boundaries
