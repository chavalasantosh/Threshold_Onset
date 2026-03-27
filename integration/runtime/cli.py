"""Shared CLI/runtime environment helpers for runner scripts."""

from __future__ import annotations

import os
from typing import Dict, Optional


def build_runtime_env(
    *,
    workers: Optional[int] = None,
    method_workers: Optional[int] = None,
    profile: bool = False,
) -> Dict[str, str]:
    """
    Build child-process environment for unified runtime controls.

    Mappings:
    - workers -> SANTEK_TEXT_WORKERS, STRESS_WORKERS
    - method_workers -> SANTEK_METHOD_WORKERS
    - profile -> PIPELINE_PROFILE
    """
    env = dict(os.environ)
    if workers is not None:
        env["SANTEK_TEXT_WORKERS"] = str(max(1, int(workers)))
        env["STRESS_WORKERS"] = str(max(1, int(workers)))
    if method_workers is not None:
        env["SANTEK_METHOD_WORKERS"] = str(max(1, int(method_workers)))
    if profile:
        env["PIPELINE_PROFILE"] = "1"
    return env
