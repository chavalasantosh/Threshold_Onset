"""async_run parity with sync run() flags."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_async_run_return_model_state():
    from integration.run_complete import PipelineConfig, async_run

    cfg = PipelineConfig.from_project()
    cfg.show_tui = False

    async def _go():
        return await async_run(
            text_override="Action before knowledge.",
            cfg=cfg,
            return_result=True,
            return_model_state=True,
        )

    result = asyncio.run(_go())
    assert result is not None
    assert result.model_state is not None
    assert "phase2_metrics" in result.model_state


def test_async_run_without_model_state():
    from integration.run_complete import PipelineConfig, async_run

    cfg = PipelineConfig.from_project()
    cfg.show_tui = False

    async def _go():
        return await async_run(
            text_override="Short.",
            cfg=cfg,
            return_result=True,
            return_model_state=False,
        )

    result = asyncio.run(_go())
    assert result is not None
    assert getattr(result, "model_state", None) is None
