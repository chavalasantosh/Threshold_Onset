# Integration Runtime (Stdlib-Only)

This package provides reusable concurrency primitives for `integration/*` modules
without third-party dependencies.

## Goals

- Keep execution model explicit and debuggable.
- Use only Python standard library.
- Centralize retries, timeout handling, and batch metrics.

## Core APIs

- `JobSpec`: typed job definition (callable + args + retries + timeout).
- `JobResult`: standardized output envelope for success/failure.
- `ExecutionConfig`: backend, worker cap, queue bound/backpressure, timeout/fail-fast.
- `RetryPolicy`: no/fast/standard retry presets.
- `run_tasks(...)`: execute a batch with `thread` or `process` backend.
- `choose_backend(...)`, `choose_workers(...)`: central selection policies.

## Example

```python
from integration.runtime import JobSpec, ExecutionConfig, RETRY_STANDARD, run_tasks

jobs = [
    JobSpec(job_id="t1", fn=some_fn, args=(1, 2), retries=1),
    JobSpec(job_id="t2", fn=some_fn, args=(3, 4), timeout_s=30),
]
cfg = ExecutionConfig(
    backend="process",
    max_workers=4,
    queue_bound=8,
    default_timeout_s=60,
    retry_policy=RETRY_STANDARD,
)
results, metrics = run_tasks(jobs, config=cfg)
```

## Rollout Plan

1. Integrate into `integration/model/santek_base.py` init fan-out.
2. Replace ad-hoc executor usage in stress/benchmark scripts.
3. Add optional checkpoint hooks in long-running jobs.
