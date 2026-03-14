"""Dataclasses for the integration runtime layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, Literal, Optional, Tuple, TypeVar

T = TypeVar("T")
R = TypeVar("R")
Backend = Literal["thread", "process"]


@dataclass(frozen=True)
class JobSpec(Generic[T, R]):
    """Single unit of work for the runtime executor."""

    job_id: str
    fn: Callable[..., R]
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = field(default_factory=dict)
    retries: int = 0
    timeout_s: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetryPolicy:
    """Retry profile for transient failures."""

    max_attempts: int = 1
    backoff_base_s: float = 0.0
    backoff_multiplier: float = 1.0
    jitter_s: float = 0.0


RETRY_NONE = RetryPolicy(max_attempts=1)
RETRY_FAST = RetryPolicy(max_attempts=2, backoff_base_s=0.1, backoff_multiplier=2.0, jitter_s=0.05)
RETRY_STANDARD = RetryPolicy(max_attempts=3, backoff_base_s=0.2, backoff_multiplier=2.0, jitter_s=0.1)


@dataclass(frozen=True)
class ExecutionConfig:
    """Execution tuning knobs for runtime batches."""

    backend: Backend = "process"
    max_workers: Optional[int] = None
    queue_bound: int = 0
    default_timeout_s: Optional[float] = None
    fail_fast: bool = False
    retry_policy: RetryPolicy = RETRY_NONE


@dataclass
class JobResult(Generic[R]):
    """Result envelope for a job execution."""

    job_id: str
    ok: bool
    value: Optional[R] = None
    error: Optional[str] = None
    attempt_count: int = 1
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunMetrics:
    """Aggregate metrics for a runtime batch."""

    submitted: int = 0
    succeeded: int = 0
    failed: int = 0
    cancelled: int = 0
    timed_out: int = 0
    retries: int = 0
    peak_in_flight: int = 0
    elapsed_ms: float = 0.0
