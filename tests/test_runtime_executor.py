"""Runtime executor regression tests."""

from __future__ import annotations

import unittest

from integration.runtime import (
    ExecutionConfig,
    JobSpec,
    RETRY_FAST,
    run_tasks,
)


def _ok(x: int) -> int:
    return x * 2


def _flaky(counter: dict) -> int:
    counter["n"] += 1
    if counter["n"] < 2:
        raise RuntimeError("transient")
    return 42


class RuntimeExecutorTests(unittest.TestCase):
    def test_thread_success_order(self) -> None:
        jobs = [JobSpec(job_id=f"j{i}", fn=_ok, args=(i,)) for i in range(5)]
        results, metrics = run_tasks(
            jobs,
            config=ExecutionConfig(backend="thread", max_workers=2),
        )
        self.assertEqual(metrics.submitted, 5)
        self.assertEqual(metrics.failed, 0)
        self.assertEqual([r.value for r in results], [0, 2, 4, 6, 8])

    def test_retry_policy(self) -> None:
        shared = {"n": 0}
        jobs = [JobSpec(job_id="retry", fn=_flaky, args=(shared,), retries=1)]
        results, metrics = run_tasks(
            jobs,
            config=ExecutionConfig(backend="thread", max_workers=1, retry_policy=RETRY_FAST),
        )
        self.assertTrue(results[0].ok)
        self.assertEqual(results[0].value, 42)
        self.assertGreaterEqual(metrics.retries, 1)


if __name__ == "__main__":
    unittest.main()
