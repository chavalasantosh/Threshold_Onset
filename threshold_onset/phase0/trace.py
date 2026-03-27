"""
Phase 0: TRACE

Only traces, patterns of survival, invariants under repetition.

NO symbols, IDs, names, interpretations.

If this returns anything interpretable → it's wrong.
"""

import threading
import time
from typing import Any, Dict, Iterable, List


def _opaque(value: float) -> float:
    """Bound trace values to stable numeric range."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


def record(value: float = 0.0):
    """
    Record a trace of action.
    Returns: raw trace data, not labeled or named.
    """
    return {
        "value": _opaque(value),
        "t_ns": float(time.perf_counter_ns()),
        "thread_id": float(threading.get_ident()),
    }


def pattern(traces: Iterable[Dict[str, Any]] = ()):
    """
    Extract pattern from traces.
    Returns: pattern structure, not meaning.
    """
    trace_list: List[Dict[str, Any]] = list(traces)
    values = [float(t.get("value", 0.0)) for t in trace_list]
    if not values:
        return {"count": 0, "mean": 0.0, "delta": 0.0}
    mean = sum(values) / len(values)
    delta = values[-1] - values[0] if len(values) > 1 else 0.0
    return {"count": len(values), "mean": mean, "delta": delta}


def invariant(traces: Iterable[Dict[str, Any]] = (), tolerance: float = 1e-9):
    """
    Find what remains constant under repetition.
    Returns: invariant structure, not explanation.
    """
    values = [float(t.get("value", 0.0)) for t in traces]
    if not values:
        return {"stable": True, "reference": 0.0, "spread": 0.0}
    spread = max(values) - min(values)
    return {
        "stable": spread <= tolerance,
        "reference": values[0],
        "spread": spread,
    }
