"""Stdlib-only runtime primitives for concurrent integration jobs."""

from integration.runtime.executor import run_tasks
from integration.runtime.models import (
    RETRY_FAST,
    RETRY_NONE,
    RETRY_STANDARD,
    ExecutionConfig,
    JobResult,
    JobSpec,
    RetryPolicy,
    RunMetrics,
)
from integration.runtime.policies import choose_backend, choose_workers

__all__ = [
    "JobSpec",
    "JobResult",
    "RunMetrics",
    "RetryPolicy",
    "ExecutionConfig",
    "RETRY_NONE",
    "RETRY_FAST",
    "RETRY_STANDARD",
    "choose_backend",
    "choose_workers",
    "run_tasks",
]
