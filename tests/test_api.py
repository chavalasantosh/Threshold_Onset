"""Integration tests for THRESHOLD_ONSET API and CLI."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Ensure project root in path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_api_process_basic():
    """API process() returns ProcessResult with expected fields."""
    from threshold_onset.api import process, ProcessResult

    result = process("Action before knowledge", silent=True)
    assert isinstance(result, ProcessResult)
    assert hasattr(result, "success")
    assert hasattr(result, "input_text")
    assert hasattr(result, "generated_outputs")
    assert hasattr(result, "token_count")
    assert hasattr(result, "identity_count")
    assert hasattr(result, "duration_seconds")


def test_api_process_success():
    """API process() succeeds with valid input."""
    from threshold_onset.api import process

    result = process("test input", silent=True)
    assert result.success
    assert result.token_count >= 1
    assert len(result.generated_outputs) >= 1


def test_api_process_empty_raises():
    """API process() raises ValidationError for empty input."""
    from threshold_onset.api import process
    from threshold_onset.exceptions import ValidationError

    with pytest.raises(ValidationError):
        process("")
    with pytest.raises(ValidationError):
        process("   ")


def test_api_process_result_to_dict():
    """ProcessResult.to_dict() is serializable."""
    from threshold_onset.api import process

    result = process("test", silent=True)
    d = result.to_dict()
    assert json.dumps(d)  # Must not raise
    assert "success" in d
    assert "token_count" in d


def test_cli_config():
    """CLI config subcommand outputs valid JSON."""
    out = subprocess.run(
        [sys.executable, "-m", "threshold_onset", "config"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert out.returncode == 0
    data = json.loads(out.stdout)
    assert "pipeline" in data


def test_cli_health():
    """CLI health subcommand outputs valid JSON."""
    out = subprocess.run(
        [sys.executable, "-m", "threshold_onset", "health"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert out.returncode == 0
    data = json.loads(out.stdout)
    assert data.get("status") == "ok"
    assert "version" in data


@pytest.mark.slow
def test_rest_process():
    """REST POST /process returns ProcessResult-like JSON (starts health server)."""
    import time
    import urllib.request

    proc = subprocess.Popen(
        [sys.executable, "scripts/health_server.py"],
        cwd=str(ROOT),
        env={**os.environ, "HEALTH_PORT": "19999"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(2.5)  # give server time to bind and accept (avoids flaky timeout)
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:19999/process",
            data=json.dumps({"text": "test"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        assert "success" in data
        assert "generated_outputs" in data
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
