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
    
    windows = [
        tuple(residues[i:i + window_size])
        for i in range(len(residues) - window_size + 1)
    ]
    repetition_count = 0
    eligible_counts = {}

    # Count non-overlapping equal windows in O(n) by activating windows
    # only after they are far enough (>= window_size) from current index.
    for idx, window in enumerate(windows):
        activate_idx = idx - window_size
        if activate_idx >= 0:
            prev_window = windows[activate_idx]
            eligible_counts[prev_window] = eligible_counts.get(prev_window, 0) + 1
        repetition_count += eligible_counts.get(window, 0)
    
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
    
    counts = {}
    for sequence in residue_sequences:
        key = tuple(sequence)
        counts[key] = counts.get(key, 0) + 1

    # Match legacy behavior: count each sequence index that has at least one
    # duplicate later, equivalent to sum(count - 1) per unique sequence.
    survival_count = sum(max(0, count - 1) for count in counts.values())

    return {'survival_count': survival_count}
