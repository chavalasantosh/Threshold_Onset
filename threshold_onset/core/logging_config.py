"""
Structured logging for THRESHOLD_ONSET.

- Configurable level (DEBUG, INFO, WARN, ERROR)
- Console + optional file handler
- Optional log file rotation (RotatingFileHandler)
- Consistent format
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
DEFAULT_BACKUP_COUNT = 5


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    log_dir: Optional[Path] = None,
    rotate: bool = True,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
        log_dir: If set and log_file not set, writes to log_dir/threshold_onset.log
        rotate: If True, use RotatingFileHandler (default 10MB, 5 backups)
        max_bytes: Max bytes per log file when rotating
        backup_count: Number of backup files to keep
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger("threshold_onset")
    root.setLevel(numeric_level)

    # Avoid duplicate handlers on repeated setup
    if root.handlers:
        return

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(numeric_level)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # File (optional)
    file_path = log_file
    if file_path is None and log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_path = log_dir / "threshold_onset.log"

    if file_path:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        if rotate:
            fh = RotatingFileHandler(
                file_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
        else:
            fh = logging.FileHandler(file_path, encoding="utf-8")
        fh.setLevel(numeric_level)
        fh.setFormatter(formatter)
        root.addHandler(fh)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module. Use threshold_onset.* namespace."""
    if not name.startswith("threshold_onset"):
        name = f"threshold_onset.{name}"
    return logging.getLogger(name)
