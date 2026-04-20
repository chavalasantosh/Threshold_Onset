"""Tests for threshold_onset.universal_input path detection."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_is_file_path_rejects_tamil_prose_with_colon():
    """Long Tamil/Unicode text with spaces and ':' must not be treated as a path."""
    from threshold_onset.universal_input import is_file_path

    s = (
        "நேரியல் இயற்கணிதத்தில் டோப்ளிட்சு அணி (Toeplitz matrix) "
        "எடுத்துக்காட்டு: n×n வரிசை"
    )
    assert is_file_path(s, ROOT) is False


def test_is_file_path_rejects_multiline():
    from threshold_onset.universal_input import is_file_path

    assert is_file_path("line1\nline2", ROOT) is False


def test_is_file_path_accepts_existing_file(tmp_path):
    from threshold_onset.universal_input import is_file_path

    f = tmp_path / "x.txt"
    f.write_text("hi", encoding="utf-8")
    assert is_file_path(str(f), tmp_path) is True


def test_is_file_path_rejects_english_prose_with_colon():
    from threshold_onset.universal_input import is_file_path

    assert (
        is_file_path(
            "See §4.7—Toeplitz: matrix notes and more words here", ROOT
        )
        is False
    )
