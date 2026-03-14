"""
THRESHOLD_ONSET — Phase 0

Action happens.
Traces remain.
Repetition reveals survival.

No meaning.
No identity.
"""

from typing import Any, Callable, Iterable, Iterator, List, Tuple


def phase0(actions: Iterable[Callable[[], Any]], steps: int) -> Iterator[Tuple[Any, int, int]]:
    """
    actions: raw callable behaviors (no labels)
    steps: number of repetitions

    Yields:
        trace, count, step_count
    """
    if steps < 0:
        raise ValueError("steps must be >= 0")

    action_list: List[Callable[[], Any]] = list(actions)
    if not action_list:
        return

    traces: List[Any] = []
    trace_count = 0
    step_count = 0

    for step in range(steps):
        _ = step  # explicit: phase0 ignores step semantics, only repetition matters.
        for action in action_list:
            trace = action()
            traces.append(trace)
            trace_count += 1
            step_count += 1

            yield trace, trace_count, step_count
