"""
Phase 0: REPETITION

Only repetition, persistence, stabilization.

NO segmentation, identity, repeatable units (those are Phase 1+).

कार्य (kārya) happens before ज्ञान (jñāna)
"""

from typing import Iterable, List


def repeat(values: Iterable[float] = (), times: int = 2):
    """
    Repetition without assuming units.
    Returns: repetition pattern, not repeated units.
    """
    base = [float(v) for v in values]
    if times <= 0:
        return []
    out: List[float] = []
    for _ in range(times):
        out.extend(base)
    return out


def stabilize(values: Iterable[float] = (), alpha: float = 0.5):
    """
    Stabilization through repetition.
    Returns: what stabilizes, not what it stabilizes into.
    """
    vals = [float(v) for v in values]
    if not vals:
        return []
    alpha = min(1.0, max(0.0, float(alpha)))
    smoothed = [vals[0]]
    for value in vals[1:]:
        smoothed.append(alpha * value + (1.0 - alpha) * smoothed[-1])
    return smoothed


def survive(values: Iterable[float] = (), threshold: float = 0.0):
    """
    What survives repetition.
    Returns: survival pattern, not identity of what survives.
    """
    thr = float(threshold)
    return [float(v) for v in values if float(v) >= thr]
