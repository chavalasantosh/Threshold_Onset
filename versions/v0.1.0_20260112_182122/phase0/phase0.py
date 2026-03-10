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

    Returns:
        raw_traces
        persistence_map
        survival_patterns
    """
    traces = []

    for _ in range(steps):
        for action in actions:
            trace = action()
            traces.append(trace)

    return traces
