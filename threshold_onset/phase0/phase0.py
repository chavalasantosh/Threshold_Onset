"""
THRESHOLD_ONSET — Phase 0

Action happens.
Traces remain.
Repetition reveals survival.

No meaning.
No identity.
"""


def phase0(actions, steps):
    """
    actions: raw callable behaviors (no labels)
    steps: number of repetitions

    Yields:
        trace, count, step_count
    """
    traces = []
    step_count = 0

    for step in range(steps):
        for action in actions:
            trace = action()
            traces.append(trace)
            step_count += 1
            
            yield trace, len(traces), step_count
