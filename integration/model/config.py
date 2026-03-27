"""
Model configuration: loaded from project config, validated.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_LEARNING_RATE = 0.1
DEFAULT_PREDICTION_METHOD = "highest_score"
VALID_PREDICTION_METHODS = ("highest_score", "weighted_random")


@dataclasses.dataclass
class ModelConfig:
    """Model layer config. Load from config/default.json under 'model'."""
    learning_rate: float = DEFAULT_LEARNING_RATE
    prediction_method: str = DEFAULT_PREDICTION_METHOD
    prediction_methods: Optional[List[str]] = None  # When set, use all (e.g. for generation).

    def validate(self) -> List[str]:
        errors: List[str] = []
        if self.learning_rate <= 0:
            errors.append("model.learning_rate must be > 0")
        if self.prediction_methods:
            for m in self.prediction_methods:
                if m not in VALID_PREDICTION_METHODS:
                    errors.append(f"model.prediction_methods entry '{m}' not in {VALID_PREDICTION_METHODS}")
                    break
        elif self.prediction_method not in VALID_PREDICTION_METHODS:
            errors.append(
                f"model.prediction_method must be one of {VALID_PREDICTION_METHODS}"
            )
        return errors

    @classmethod
    def from_project(cls, project_root: Optional[Path] = None) -> "ModelConfig":
        """Load from project config; merge 'model' section. Sensible defaults if no config."""
        cfg = cls()
        raw: Dict[str, Any] = {}
        try:
            from threshold_onset.config import get_config  # type: ignore
            raw = get_config()
        except Exception:  # type: ignore
            pass
        model_section = raw.get("model", {})
        if isinstance(model_section, dict):
            if "learning_rate" in model_section:
                cfg.learning_rate = float(model_section["learning_rate"])
            if "prediction_method" in model_section:
                cfg.prediction_method = str(model_section["prediction_method"])
            if "prediction_methods" in model_section:
                cfg.prediction_methods = list(model_section["prediction_methods"])
        return cfg
