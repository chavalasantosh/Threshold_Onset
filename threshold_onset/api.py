"""
THRESHOLD_ONSET — Programmatic API

Clean Python API for embedding the pipeline in other applications.
"""

import importlib
import logging
import os
import sys
import time
import contextlib
import io
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from threshold_onset.config import get_config
from threshold_onset.exceptions import ValidationError
from threshold_onset.line_codec import encode as encode_compact


# Default max input length (chars) to prevent abuse
DEFAULT_MAX_INPUT_LENGTH = 1_000_000
DEFAULT_TIMEOUT_SECONDS = 0.0
DEFAULT_MAX_REQUEST_BODY_BYTES = 2_000_000

LOG = logging.getLogger("threshold_onset.api")


@dataclass
class ProcessResult:
    """Result of pipeline processing."""

    success: bool
    input_text: str
    generated_outputs: List[str]
    token_count: int
    identity_count: int
    duration_seconds: float
    metrics: Dict[str, Any]
    trace_id: str = ""
    error_code: Optional[str] = None
    error: Optional[str] = None
    # Present only when process(..., return_model_state=True). Can be large.
    model_state: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        out: Dict[str, Any] = {
            "success": self.success,
            "input_text": self.input_text,
            "generated_outputs": self.generated_outputs,
            "token_count": self.token_count,
            "identity_count": self.identity_count,
            "duration_seconds": self.duration_seconds,
            "metrics": self.metrics,
            "trace_id": self.trace_id,
            "error_code": self.error_code,
            "error": self.error,
        }
        if self.model_state is not None:
            out["model_state"] = self.model_state
        return out


def _new_trace_id() -> str:
    return uuid.uuid4().hex[:16]


def _compact_log(event: str, trace_id: str, **fields: Any) -> None:
    payload = {"event": event, "trace_id": trace_id, **fields}
    try:
        LOG.info(encode_compact(payload, sort_keys=True).rstrip("\n"))
    except Exception:
        # Keep API robust even when logging sinks are misconfigured.
        pass


def _parse_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _classify_error(exc: Exception) -> str:
    """Map exceptions to stable failure taxonomy codes."""
    name = type(exc).__name__
    text = str(exc).lower()
    if isinstance(exc, ValidationError):
        return "input_validation"
    if "phase 2 gate failed" in text or "phase 3 gate failed" in text or "phase 4 gate failed" in text:
        return "phase_gate_failure"
    if "scoring" in text or "contract" in text:
        return "scoring_contract"
    if "timeout" in text or "timed out" in text:
        return "runtime_timeout"
    if "import" in name.lower() or "import" in text:
        return "runtime_import"
    return "runtime_error"


def _resolve_pipeline_settings(
    config: Optional[Dict[str, Any]],
    *,
    max_input_length: int,
    timeout_seconds: float,
) -> Tuple[Dict[str, Any], Dict[str, Any], int, float]:
    cfg = config or get_config()
    pipeline_cfg = cfg.get("pipeline", {})
    effective_max_len = _parse_int(pipeline_cfg.get("max_input_length", max_input_length), max_input_length)
    effective_timeout = _parse_float(
        pipeline_cfg.get("api_timeout_seconds", timeout_seconds),
        timeout_seconds,
    )
    if effective_timeout < 0:
        effective_timeout = 0.0
    return cfg, pipeline_cfg, effective_max_len, effective_timeout


def _load_run_complete() -> Tuple[Any, Any]:
    module = importlib.import_module("integration.run_complete")
    return getattr(module, "run"), getattr(module, "PipelineConfig")


def process(
    text: str,
    config: Optional[Dict[str, Any]] = None,
    *,
    max_input_length: int = DEFAULT_MAX_INPUT_LENGTH,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    silent: bool = True,
    trace_id: Optional[str] = None,
    return_model_state: bool = False,
    include_phase10_metrics: bool = False,
) -> ProcessResult:
    """
    Process text through the full pipeline.

    Args:
        text: Input text to process.
        config: Optional config override. If None, uses get_config().
        max_input_length: Maximum allowed input length (chars). Raises ValidationError if exceeded.
        silent: If True, suppress pipeline stdout (for programmatic use).
        return_model_state: If True, ``ProcessResult.model_state`` is set (same shape as
            ``integration.run_complete.run(..., return_model_state=True)``).
        include_phase10_metrics: If True, sets ``PipelineConfig.include_phase10_metrics`` so
            ``model_state`` may include ``phase10_metrics`` (only when ``return_model_state`` is True).

    Returns:
        ProcessResult with success, outputs, and metrics.

    Raises:
        ValidationError: If input is empty or exceeds max_input_length.
    """
    text = (text or "").strip()
    if not text:
        raise ValidationError("Input text cannot be empty", details={"input_length": 0})

    trace = trace_id or _new_trace_id()
    cfg, pipeline_cfg, effective_max_len, effective_timeout = _resolve_pipeline_settings(
        config,
        max_input_length=max_input_length,
        timeout_seconds=timeout_seconds,
    )
    tokenization_method = pipeline_cfg.get("tokenization_method", "word")
    num_runs = pipeline_cfg.get("num_runs", 3)
    if len(text) > effective_max_len:
        raise ValidationError(
            f"Input exceeds max length ({effective_max_len} chars)",
            details={"input_length": len(text), "max_length": effective_max_len},
        )

    # Ensure project root and integration in path (run_complete imports surface, scoring, etc.)
    project_root = Path(__file__).resolve().parent.parent
    integration_dir = project_root / "integration"
    for p in (str(integration_dir), str(project_root)):
        if p not in sys.path:
            sys.path.insert(0, p)

    start = time.perf_counter()
    _compact_log(
        "process_started",
        trace,
        input_chars=len(text),
        tokenization_method=tokenization_method,
        num_runs=num_runs,
        timeout_seconds=effective_timeout,
        silent=bool(silent),
    )

    try:
        capture_out = io.StringIO()
        capture_err = io.StringIO()
        run_complete_run, pipeline_config_type = _load_run_complete()
        run_cfg = pipeline_config_type.from_project()
        run_cfg.show_tui = False if silent else run_cfg.show_tui
        if "tokenization_method" in pipeline_cfg:
            run_cfg.tokenization_method = str(pipeline_cfg["tokenization_method"])
        if "num_runs" in pipeline_cfg:
            run_cfg.num_runs = _parse_int(pipeline_cfg["num_runs"], run_cfg.num_runs)
        if include_phase10_metrics:
            run_cfg.include_phase10_metrics = True

        def _invoke_run() -> Any:
            with (
                contextlib.redirect_stdout(capture_out) if silent else contextlib.nullcontext(),
                contextlib.redirect_stderr(capture_err) if silent else contextlib.nullcontext(),
            ):
                return run_complete_run(
                    text_override=text,
                    cfg=run_cfg,
                    learner=None,
                    return_result=True,
                    return_model_state=bool(return_model_state),
                )

        if effective_timeout > 0:
            executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="threshold_onset_api")
            future = executor.submit(_invoke_run)
            try:
                out = future.result(timeout=effective_timeout)
            except FuturesTimeoutError:
                future.cancel()
                # Do not wait on running worker after timeout; return promptly.
                executor.shutdown(wait=False, cancel_futures=True)
                raise
            else:
                executor.shutdown(wait=True, cancel_futures=False)
        else:
            out = _invoke_run()

        if out is not None:
            elapsed = time.perf_counter() - start
            _compact_log(
                "process_succeeded",
                trace,
                duration_seconds=elapsed,
                token_count=int(out.token_count),
                identity_count=int(out.identity_count),
                output_count=len(out.generated_outputs),
            )
            ms = getattr(out, "model_state", None) if return_model_state else None
            return ProcessResult(
                success=True,
                input_text=out.input_text,
                generated_outputs=out.generated_outputs,
                token_count=out.token_count,
                identity_count=out.identity_count,
                duration_seconds=elapsed,
                metrics={
                    "tokenization_method": tokenization_method,
                    "num_runs": num_runs,
                    "timeout_seconds": effective_timeout,
                    "return_model_state": bool(return_model_state),
                    "include_phase10_metrics": bool(include_phase10_metrics),
                },
                trace_id=trace,
                error_code=None,
                model_state=ms if isinstance(ms, dict) else None,
            )

    except FuturesTimeoutError:
        elapsed = time.perf_counter() - start
        _compact_log("process_timeout", trace, duration_seconds=elapsed, timeout_seconds=effective_timeout)
        return ProcessResult(
            success=False,
            input_text=text,
            generated_outputs=[],
            token_count=0,
            identity_count=0,
            duration_seconds=elapsed,
            metrics={"timeout_seconds": effective_timeout},
            trace_id=trace,
            error_code="runtime_timeout",
            error=f"processing timed out after {effective_timeout:.2f}s",
        )
    except Exception as e:
        elapsed = time.perf_counter() - start
        code = _classify_error(e)
        _compact_log("process_failed", trace, duration_seconds=elapsed, error_code=code, error=str(e))
        return ProcessResult(
            success=False,
            input_text=text,
            generated_outputs=[],
            token_count=0,
            identity_count=0,
            duration_seconds=elapsed,
            metrics={},
            trace_id=trace,
            error_code=code,
            error=str(e),
        )

    elapsed = time.perf_counter() - start
    _compact_log("process_no_result", trace, duration_seconds=elapsed)
    return ProcessResult(
        success=False,
        input_text=text,
        generated_outputs=[],
        token_count=0,
        identity_count=0,
        duration_seconds=elapsed,
        metrics={},
        trace_id=trace,
        error_code="pipeline_no_result",
        error="Pipeline returned no result",
    )
