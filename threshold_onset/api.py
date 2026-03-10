"""
THRESHOLD_ONSET — Programmatic API

Clean Python API for embedding the pipeline in other applications.
"""

import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from threshold_onset.config import get_config
from threshold_onset.exceptions import ValidationError


# Default max input length (chars) to prevent abuse
DEFAULT_MAX_INPUT_LENGTH = 1_000_000


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
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "input_text": self.input_text,
            "generated_outputs": self.generated_outputs,
            "token_count": self.token_count,
            "identity_count": self.identity_count,
            "duration_seconds": self.duration_seconds,
            "metrics": self.metrics,
            "error": self.error,
        }


def process(
    text: str,
    config: Optional[Dict[str, Any]] = None,
    *,
    max_input_length: int = DEFAULT_MAX_INPUT_LENGTH,
    silent: bool = True,
) -> ProcessResult:
    """
    Process text through the full pipeline.

    Args:
        text: Input text to process.
        config: Optional config override. If None, uses get_config().
        max_input_length: Maximum allowed input length (chars). Raises ValidationError if exceeded.
        silent: If True, suppress pipeline stdout (for programmatic use).

    Returns:
        ProcessResult with success, outputs, and metrics.

    Raises:
        ValidationError: If input is empty or exceeds max_input_length.
    """
    text = (text or "").strip()
    if not text:
        raise ValidationError("Input text cannot be empty", details={"input_length": 0})

    cfg = config or get_config()
    pipeline_cfg = cfg.get("pipeline", {})
    tokenization_method = pipeline_cfg.get("tokenization_method", "word")
    num_runs = pipeline_cfg.get("num_runs", 3)
    effective_max_len = pipeline_cfg.get("max_input_length", max_input_length)
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

    try:
        from integration.run_complete import main as run_complete_main  # pylint: disable=import-outside-toplevel

        if silent:
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()

        try:
            out = run_complete_main(
                learner=None,
                return_result=True,
                text_override=text,
            )
        finally:
            if silent:
                sys.stdout = old_stdout

        if out is not None:
            return ProcessResult(
                success=True,
                input_text=out.get("input_text", text),
                generated_outputs=out.get("generated_outputs", []),
                token_count=out.get("token_count", 0),
                identity_count=out.get("identity_count", 0),
                duration_seconds=time.perf_counter() - start,
                metrics={
                    "tokenization_method": tokenization_method,
                    "num_runs": num_runs,
                },
            )

    except Exception as e:
        return ProcessResult(
            success=False,
            input_text=text,
            generated_outputs=[],
            token_count=0,
            identity_count=0,
            duration_seconds=time.perf_counter() - start,
            metrics={},
            error=str(e),
        )

    return ProcessResult(
        success=False,
        input_text=text,
        generated_outputs=[],
        token_count=0,
        identity_count=0,
        duration_seconds=time.perf_counter() - start,
        metrics={},
        error="Pipeline returned no result",
    )
