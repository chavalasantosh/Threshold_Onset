"""
THRESHOLD_ONSET — Phase 1: DISTANCE

Difference measurement between residues.
Returns raw numbers only. No interpretation.

CONSTRAINT: Distance metrics must be mechanically defined.
No adaptive or learned metrics.
"""


def absolute_difference(a, b):
    """
    Compute absolute difference between two residues.
    
    Args:
        a: residue (float)
        b: residue (float)
    
    Returns:
        Absolute difference (float, raw number)
    """
    return abs(a - b)


def pairwise_distances(residues):
    """
    Compute pairwise distances between consecutive residues.
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
    
    Returns:
        List of distance measurements (raw numbers, no interpretation)
    """
    if len(residues) < 2:
        return []
    
    distances = []
    for i in range(len(residues) - 1):
        dist = absolute_difference(residues[i], residues[i + 1])
        distances.append(dist)
    
    return distances
