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
    assert "trace_id" in d


def test_api_process_trace_id_passthrough():
    """API process() should preserve caller-provided trace id."""
    from threshold_onset.api import process

    result = process("test", silent=True, trace_id="abc123traceid000")
    assert result.trace_id == "abc123traceid000"
    assert result.to_dict()["trace_id"] == "abc123traceid000"


def test_api_process_return_model_state_optional():
    """process(return_model_state=True) attaches model_state; phase10 optional."""
    from threshold_onset.api import process

    result = process(
        "Action before knowledge.",
        silent=True,
        return_model_state=True,
        include_phase10_metrics=True,
    )
    assert result.success
    assert result.model_state is not None
    assert "phase2_metrics" in result.model_state
    assert "phase10_metrics" in result.model_state
    assert result.model_state["phase10_metrics"].get("phase") == "phase10"


def test_cli_config():
    """CLI config subcommand prints parseable compact line text."""
    out = subprocess.run(
        [sys.executable, "-m", "threshold_onset", "config"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert out.returncode == 0
    from threshold_onset.line_codec import decode_document

    data = decode_document(out.stdout)
    assert "pipeline" in data


def test_cli_health():
    """CLI health subcommand prints parseable compact line text."""
    out = subprocess.run(
        [sys.executable, "-m", "threshold_onset", "health"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert out.returncode == 0
    from threshold_onset.line_codec import decode_document

    data = decode_document(out.stdout)
    assert data.get("status") == "ok"
    assert "version" in data


@pytest.mark.slow
def test_rest_process():
    """REST POST /process returns ProcessResult-shaped body in compact line text."""
    import socket
    import time
    import urllib.request
    import urllib.error

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    base_url = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen(
        [sys.executable, "scripts/health_server.py"],
        cwd=str(ROOT),
        env={**os.environ, "HEALTH_PORT": str(port)},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait until server is actually ready.
    ready = False
    for _ in range(40):
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=1.5) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(0.25)

    assert ready, "health server did not become ready in time"
    try:
        from threshold_onset.line_codec import decode_document

        with urllib.request.urlopen(f"{base_url}/ready", timeout=5) as resp:
            ready_data = decode_document(resp.read().decode())
        assert "ready" in ready_data
        assert "config_loaded" in ready_data

        req = urllib.request.Request(
            f"{base_url}/process",
            data=json.dumps({"text": "test"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = decode_document(resp.read().decode())
            response_trace = resp.headers.get("X-Trace-Id")
        assert "success" in data
        assert "generated_outputs" in data
        assert "trace_id" in data
        assert response_trace
        assert data["trace_id"] == response_trace
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
