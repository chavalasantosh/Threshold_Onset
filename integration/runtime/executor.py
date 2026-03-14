"""Process/thread execution helpers with retries, backpressure, and metrics."""

from __future__ import annotations

import concurrent.futures
import random
import time
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from integration.runtime.models import (
    RETRY_NONE,
    ExecutionConfig,
    JobResult,
    JobSpec,
    RetryPolicy,
    RunMetrics,
)
from integration.runtime.policies import choose_workers

ProgressCallback = Callable[[RunMetrics, JobResult], None]


def _run_job_with_retries(job: JobSpec, policy: RetryPolicy) -> JobResult:
    start = time.time()
    attempts = max(1, int(policy.max_attempts), int(job.retries) + 1)
    last_error: Optional[str] = None
    for attempt in range(1, attempts + 1):
        try:
            value = job.fn(*job.args, **job.kwargs)
            return JobResult(
                job_id=job.job_id,
                ok=True,
                value=value,
                attempt_count=attempt,
                duration_ms=(time.time() - start) * 1000.0,
                metadata=dict(job.metadata),
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            last_error = str(exc)
            if attempt < attempts:
                sleep_s = policy.backoff_base_s * (policy.backoff_multiplier ** (attempt - 1))
                if policy.jitter_s > 0:
                    sleep_s += random.uniform(0.0, policy.jitter_s)
                if sleep_s > 0:
                    time.sleep(sleep_s)
    return JobResult(
        job_id=job.job_id,
        ok=False,
        error=last_error or "unknown error",
        attempt_count=attempts,
        duration_ms=(time.time() - start) * 1000.0,
        metadata=dict(job.metadata),
    )


def run_tasks(
    jobs: Iterable[JobSpec],
    *,
    backend: str = "process",
    max_workers: Optional[int] = None,
    config: Optional[ExecutionConfig] = None,
    progress_callback: Optional[ProgressCallback] = None,
) -> tuple[List[JobResult], RunMetrics]:
    """
    Run a batch of jobs with the selected backend.

    Notes:
    - Use backend='process' for CPU-heavy tasks.
    - Use backend='thread' for I/O-heavy tasks.
    """
    cfg = config or ExecutionConfig(
        backend=backend if backend in ("thread", "process") else "process",
        max_workers=max_workers,
        retry_policy=RETRY_NONE,
    )
    job_list = list(jobs)
    metrics = RunMetrics(submitted=len(job_list))
    if not job_list:
        return [], metrics

    workers = choose_workers(
        submitted=len(job_list),
        backend=cfg.backend,
        max_workers=cfg.max_workers if cfg.max_workers is not None else max_workers,
    )
    start = time.time()
    results: Dict[str, JobResult] = {}
    submitted_idx = 0
    in_flight: Dict[concurrent.futures.Future, Tuple[JobSpec, float]] = {}
    queue_bound = cfg.queue_bound if cfg.queue_bound > 0 else workers
    queue_bound = max(queue_bound, workers)

    executor_cls = (
        concurrent.futures.ProcessPoolExecutor
        if cfg.backend == "process"
        else concurrent.futures.ThreadPoolExecutor
    )
    with executor_cls(max_workers=workers) as executor:
        while submitted_idx < len(job_list) and len(in_flight) < queue_bound:
            job = job_list[submitted_idx]
            fut = executor.submit(_run_job_with_retries, job, cfg.retry_policy)
            in_flight[fut] = (job, time.time())
            submitted_idx += 1
        metrics.peak_in_flight = max(metrics.peak_in_flight, len(in_flight))

        while in_flight:
            done, _pending = concurrent.futures.wait(
                in_flight.keys(),
                return_when=concurrent.futures.FIRST_COMPLETED,
                timeout=0.2,
            )

            # Cooperative timeout/cancellation check
            now = time.time()
            for future, (job, started_at) in list(in_flight.items()):
                timeout_s = job.timeout_s if job.timeout_s is not None else cfg.default_timeout_s
                if timeout_s is None:
                    continue
                if (now - started_at) > timeout_s and not future.done():
                    cancelled = future.cancel()
                    if cancelled:
                        result = JobResult(
                            job_id=job.job_id,
                            ok=False,
                            error=f"timeout after {timeout_s}s",
                            duration_ms=(now - started_at) * 1000.0,
                            metadata=dict(job.metadata),
                        )
                        results[result.job_id] = result
                        metrics.timed_out += 1
                        metrics.cancelled += 1
                        in_flight.pop(future, None)
                        if progress_callback is not None:
                            progress_callback(metrics, result)

            for future in done:
                if future not in in_flight:
                    continue
                job, _started = in_flight.pop(future)
                timeout_s = job.timeout_s if job.timeout_s is not None else cfg.default_timeout_s
                if timeout_s is not None and future.cancelled():
                    result = JobResult(
                        job_id=job.job_id,
                        ok=False,
                        error=f"timeout after {timeout_s}s",
                        duration_ms=0.0,
                        metadata=dict(job.metadata),
                    )
                    results[result.job_id] = result
                    metrics.timed_out += 1
                    metrics.cancelled += 1
                    if progress_callback is not None:
                        progress_callback(metrics, result)
                    continue

                try:
                    result = future.result()
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    result = JobResult(
                        job_id=job.job_id,
                        ok=False,
                        error=str(exc),
                        duration_ms=0.0,
                        metadata=dict(job.metadata),
                    )
                results[result.job_id] = result
                metrics.retries += max(0, result.attempt_count - 1)
                if progress_callback is not None:
                    progress_callback(metrics, result)

                if cfg.fail_fast and not result.ok:
                    for pending in list(in_flight.keys()):
                        pending.cancel()
                    in_flight.clear()
                    break

            while submitted_idx < len(job_list) and len(in_flight) < queue_bound:
                job = job_list[submitted_idx]
                fut = executor.submit(_run_job_with_retries, job, cfg.retry_policy)
                in_flight[fut] = (job, time.time())
                submitted_idx += 1
            metrics.peak_in_flight = max(metrics.peak_in_flight, len(in_flight))

    ordered: List[JobResult] = []
    for job in job_list:
        if job.job_id in results:
            ordered.append(results[job.job_id])
            continue
        ordered.append(
            JobResult(
                job_id=job.job_id,
                ok=False,
                error="not executed (fail_fast or cancelled)",
                metadata=dict(job.metadata),
            )
        )
        metrics.cancelled += 1
    metrics.succeeded = sum(1 for r in ordered if r.ok)
    metrics.failed = metrics.submitted - metrics.succeeded
    metrics.elapsed_ms = (time.time() - start) * 1000.0
    return ordered, metrics
