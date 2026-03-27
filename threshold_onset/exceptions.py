"""
THRESHOLD_ONSET — Enterprise Exception Hierarchy

Error codes and structured exceptions for programmatic handling.
"""


class ThresholdOnsetError(Exception):
    """Base exception for THRESHOLD_ONSET. All project exceptions inherit from this."""

    def __init__(self, message: str, code: str = "THRESHOLD_ONSET_ERROR", details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        base = f"[{self.code}] {self.message}"
        if self.details:
            parts = ", ".join(f"{k}={v}" for k, v in self.details.items())
            base = f"{base} ({parts})"
        return base


class ConfigError(ThresholdOnsetError):
    """Configuration load or validation failed."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, code="CONFIG_ERROR", details=details)


class PipelineError(ThresholdOnsetError):
    """Pipeline execution failed."""

    def __init__(self, message: str, phase: str = None, details: dict = None):
        super().__init__(message, code="PIPELINE_ERROR", details=details or {})
        if phase:
            self.details["phase"] = phase


class ValidationError(ThresholdOnsetError):
    """Input or output validation failed."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


# Exit codes for CLI
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_CONFIG_ERROR = 2
