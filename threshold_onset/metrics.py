"""
THRESHOLD_ONSET — Metrics Collection

Pipeline duration, token count, identity count. Optional Prometheus-style export.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class PipelineMetrics:
    """Metrics from a single pipeline run."""

    duration_seconds: float
    token_count: int
    identity_count: int
    success: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for logging/serialization."""
        return {
            "duration_seconds": self.duration_seconds,
            "token_count": self.token_count,
            "identity_count": self.identity_count,
            "success": self.success,
            **self.extra,
        }

    def to_prometheus_lines(self, prefix: str = "threshold_onset") -> str:
        """
        Export as Prometheus-style text (for scraping).
        Use prefix to namespace metrics.
        """
        lines = [
            f"# HELP {prefix}_duration_seconds Pipeline duration in seconds",
            f"# TYPE {prefix}_duration_seconds gauge",
            f"{prefix}_duration_seconds {self.duration_seconds}",
            f"# HELP {prefix}_token_count Number of tokens",
            f"# TYPE {prefix}_token_count gauge",
            f"{prefix}_token_count {self.token_count}",
            f"# HELP {prefix}_identity_count Number of identities",
            f"# TYPE {prefix}_identity_count gauge",
            f"{prefix}_identity_count {self.identity_count}",
            f"# HELP {prefix}_success Pipeline success (1=ok, 0=fail)",
            f"# TYPE {prefix}_success gauge",
            f"{prefix}_success {1 if self.success else 0}",
        ]
        return "\n".join(lines)


def collect_from_result(result: Any) -> PipelineMetrics:
    """
    Build PipelineMetrics from a ProcessResult (api.process return value).
    """
    return PipelineMetrics(
        duration_seconds=getattr(result, "duration_seconds", 0.0),
        token_count=getattr(result, "token_count", 0),
        identity_count=getattr(result, "identity_count", 0),
        success=getattr(result, "success", False),
        extra=getattr(result, "metrics", {}) or {},
    )
