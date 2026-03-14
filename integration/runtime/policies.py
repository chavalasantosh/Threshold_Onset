"""Backend and worker selection policies for runtime execution."""

from __future__ import annotations

import os
from typing import Literal, Optional

from integration.runtime.models import Backend

WorkloadHint = Literal["cpu", "io", "mixed"]


def choose_backend(hint: WorkloadHint) -> Backend:
    """Choose default backend from workload hint."""
    if hint == "io":
        return "thread"
    if hint == "mixed":
        # Mixed defaults to process because this codebase is CPU-heavy.
        return "process"
    return "process"


def choose_workers(
    submitted: int,
    *,
    backend: Backend,
    max_workers: Optional[int] = None,
) -> int:
    """Select worker count with safe caps."""
    if submitted <= 0:
        return 1
    if max_workers is not None:
        return max(1, min(int(max_workers), submitted))

    cpu = os.cpu_count() or 4
    if backend == "thread":
        return max(1, min(submitted, cpu * 2))
    return max(1, min(submitted, max(1, cpu - 1)))
