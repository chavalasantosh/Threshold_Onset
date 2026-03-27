"""
Configuration loader with environment overrides.

Uses stdlib only. Config file: JSON.
Environment: THRESHOLD_ONSET_CONFIG, THRESHOLD_ONSET_TOKENIZATION, THRESHOLD_ONSET_NUM_RUNS, etc.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from threshold_onset.exceptions import ConfigError

_CONFIG: Optional[Dict[str, Any]] = None


def _default_config_path() -> Path:
    """Path to default config file (next to project root)."""
    # threshold_onset/config/loader.py -> project_root/config/default.json
    here = Path(__file__).resolve().parent
    project_root = here.parent.parent
    return project_root / "config" / "default.json"


def _load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file. Raises ConfigError on failure."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}", details={"path": str(path)})
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config: {e}", details={"path": str(path)})


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides. Non-destructive copy."""
    result = json.loads(json.dumps(config))  # deep copy

    # THRESHOLD_ONSET_TOKENIZATION
    val = os.environ.get("THRESHOLD_ONSET_TOKENIZATION")
    if val is not None and "pipeline" in result:
        result["pipeline"]["tokenization_method"] = val

    # THRESHOLD_ONSET_NUM_RUNS
    val = os.environ.get("THRESHOLD_ONSET_NUM_RUNS")
    if val is not None:
        try:
            n = int(val)
            if "pipeline" in result:
                result["pipeline"]["num_runs"] = n
            if "benchmark" in result:
                result["benchmark"]["num_runs"] = n
        except ValueError:
            pass  # ignore invalid env

    # THRESHOLD_ONSET_LOG_LEVEL
    val = os.environ.get("THRESHOLD_ONSET_LOG_LEVEL")
    if val is not None and "pipeline" in result:
        result["pipeline"]["log_level"] = val.upper()

    # THRESHOLD_ONSET_OUTPUT_DIR
    val = os.environ.get("THRESHOLD_ONSET_OUTPUT_DIR")
    if val is not None and "pipeline" in result:
        result["pipeline"]["output_dir"] = val

    return result


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from file with environment overrides.

    Args:
        config_path: Path to JSON config. If None, uses THRESHOLD_ONSET_CONFIG
                     env var or config/default.json.

    Returns:
        Merged configuration dict.

    Raises:
        ConfigError: On load or validation failure.
    """
    global _CONFIG

    path = config_path
    if path is None:
        env_path = os.environ.get("THRESHOLD_ONSET_CONFIG")
        path = Path(env_path) if env_path else _default_config_path()

    path = Path(path).resolve()
    config = _load_json(path)
    config = _apply_env_overrides(config)
    _CONFIG = config
    return config


def get_config() -> Dict[str, Any]:
    """
    Return current config. Loads default if not yet loaded.
    """
    global _CONFIG
    if _CONFIG is None:
        load_config()
    return _CONFIG  # type: ignore
