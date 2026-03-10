"""
THRESHOLD_ONSET — Phase 1: PATTERN

Pattern detection without naming or interpretation.
Detects repetition using exact equality only.
Returns counts only. No pattern names, no abstraction.

CONSTRAINT: Pattern detection limited to EXACT EQUALITY or FIXED-WINDOW comparison.
No abstraction, compression, or symbolic patterning allowed.
"""

# FIXED window size for pattern detection (non-adaptive)
# This value is external and fixed
PATTERN_WINDOW_SIZE = 2


def detect_repetition(residues, window_size=PATTERN_WINDOW_SIZE):
    """
    Detect exact repetition in residue sequences.
    
    Uses EXACT EQUALITY only. No approximate matching.
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
        window_size: fixed window size for comparison (default: PATTERN_WINDOW_SIZE)
    
    Returns:
        Dictionary with:
        - 'repetition_count': number of exact repetitions found (int)
    """
    if len(residues) < window_size * 2:
        return {'repetition_count': 0}
    
    repetition_count = 0
    
    # Compare all pairs of windows using EXACT EQUALITY
    for i in range(len(residues) - window_size + 1):
        window1 = residues[i:i + window_size]
        for j in range(i + window_size, len(residues) - window_size + 1):
            window2 = residues[j:j + window_size]
            # EXACT EQUALITY comparison only
            if window1 == window2:
                repetition_count += 1
    
    return {'repetition_count': repetition_count}


def detect_survival(residue_sequences):
    """
    Detect sequences that survive across iterations using exact equality.
    
    Uses EXACT EQUALITY only. No pattern abstraction.
    
    Args:
        residue_sequences: list of residue sequences (each is a list of floats)
    
    Returns:
        Dictionary with:
        - 'survival_count': number of sequences that appear in multiple iterations (int)
    """
    if len(residue_sequences) < 2:
        return {'survival_count': 0}
    
    survival_count = 0
    
    # Compare sequences using EXACT EQUALITY
    for i in range(len(residue_sequences)):
        seq1 = residue_sequences[i]
        for j in range(i + 1, len(residue_sequences)):
            seq2 = residue_sequences[j]
            # EXACT EQUALITY comparison only
            if seq1 == seq2:
                survival_count += 1
                break  # Count each sequence only once
    
    return {'survival_count': survival_count}
