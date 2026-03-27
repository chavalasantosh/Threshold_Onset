"""
Phase 0: ACTION

Only action, interaction, trace, repetition, persistence, stabilization.

NO symbols, letters, meaning, tokens, embeddings, plots, coordinates.

कार्य (kārya) happens before ज्ञान (jñāna)
"""

import threading
import time
from typing import Any, Dict, Optional


def _base_trace(kind: str, *, value: Optional[float] = None) -> Dict[str, Any]:
    """
    Minimal opaque trace payload for phase-0 compatibility.
    """
    return {
        "kind": kind,
        "t_ns": float(time.perf_counter_ns()),
        "thread_id": float(threading.get_ident()),
        "value": float(value if value is not None else 0.0),
    }


def execute(value: Optional[float] = None):
    """
    Action without interpretation.
    Returns: trace of what happened, not what it means.
    """
    return _base_trace("execute", value=value)


def interact(left: Optional[float] = None, right: Optional[float] = None):
    """
    Interaction between actions.
    Returns: pattern of interaction, not identity.
    """
    if left is None and right is None:
        combined = 0.0
    else:
        combined = float((left or 0.0) + (right or 0.0))
    return _base_trace("interact", value=combined)


def persist(previous: Optional[float] = None, decay: float = 0.99):
    """
    Persistence of action over time.
    Returns: what survives, not why it survives.
    """
    baseline = float(previous if previous is not None else 1.0)
    survived = baseline * float(decay)
    return _base_trace("persist", value=survived)
