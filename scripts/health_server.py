#!/usr/bin/env python3
"""
Minimal HTTP server for THRESHOLD_ONSET.

- GET /health, /ready — Health status (JSON)
- POST /process — Process text. Body: {"text": "..."}

Uses stdlib http.server only. Port 8080 (or HEALTH_PORT env).

Usage:
    python scripts/health_server.py
    HEALTH_PORT=9090 python scripts/health_server.py
"""

import json
import logging
import sys
import time
import uuid
from pathlib import Path

# Ensure project root in path
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import import_module
from urllib.parse import urlparse

from threshold_onset.api import (
    DEFAULT_MAX_INPUT_LENGTH,
    DEFAULT_TIMEOUT_SECONDS,
    process,
)

LOG = logging.getLogger("health_server")
STARTED_AT = time.time()
DEFAULT_BODY_LIMIT = 2_000_000


def _new_trace_id() -> str:
    return uuid.uuid4().hex[:16]


def _json_log(event: str, trace_id: str, **fields):
    payload = {"event": event, "trace_id": trace_id, **fields}
    try:
        LOG.info(json.dumps(payload, ensure_ascii=True, sort_keys=True))
    except Exception:
        pass


def get_health_status():
    """Return health status dict."""
    try:
        from threshold_onset.config import get_config
        from threshold_onset import __version__
        get_config()
        return {
            "status": "ok",
            "version": __version__,
            "config_loaded": True,
            "uptime_seconds": round(time.time() - STARTED_AT, 3),
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "config_loaded": False,
            "uptime_seconds": round(time.time() - STARTED_AT, 3),
        }


def get_readiness_status():
    """Return readiness status dict."""
    base = get_health_status()
    ready = bool(base.get("status") == "ok")
    import_error = ""
    if ready:
        try:
            import_module("integration.run_complete")
        except Exception as exc:
            ready = False
            import_error = str(exc)
    return {
        **base,
        "ready": ready,
        "import_error": import_error if import_error else None,
    }


class HealthHandler(BaseHTTPRequestHandler):
    """Handle /health, /ready, and POST /process."""

    def _json_response(self, data, code=200, trace_id=""):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if trace_id:
            self.send_header("X-Trace-Id", trace_id)
        self.end_headers()
        self.wfile.write(body)

    def _trace_id(self):
        return self.headers.get("X-Trace-Id", "").strip() or _new_trace_id()

    def do_GET(self):
        trace_id = self._trace_id()
        parsed = urlparse(self.path)
        if parsed.path in ("/health", "/"):
            status = get_health_status()
            code = 200 if status.get("status") == "ok" else 503
            _json_log("http_get_health", trace_id, status_code=code)
            self._json_response(status, code, trace_id=trace_id)
        elif parsed.path == "/ready":
            status = get_readiness_status()
            code = 200 if status.get("ready") else 503
            _json_log("http_get_ready", trace_id, status_code=code)
            self._json_response(status, code, trace_id=trace_id)
        else:
            _json_log("http_get_not_found", trace_id, path=parsed.path, status_code=404)
            self._json_response({"error": "not_found", "trace_id": trace_id}, 404, trace_id=trace_id)

    def do_POST(self):
        trace_id = self._trace_id()
        parsed = urlparse(self.path)
        if parsed.path == "/process":
            try:
                content_len = int(self.headers.get("Content-Length", "0") or 0)
                max_body_bytes = int(os.environ.get("HEALTH_MAX_BODY_BYTES", str(DEFAULT_BODY_LIMIT)))
                if content_len > max_body_bytes:
                    _json_log("http_post_rejected_body_too_large", trace_id, content_len=content_len)
                    self._json_response(
                        {"error": "body_too_large", "trace_id": trace_id, "max_body_bytes": max_body_bytes},
                        413,
                        trace_id=trace_id,
                    )
                    return
                raw = self.rfile.read(content_len).decode("utf-8")
                payload = json.loads(raw) if raw else {}
                text = payload.get("text", "")
                max_input_length = int(payload.get("max_input_length", DEFAULT_MAX_INPUT_LENGTH))
                timeout_seconds = float(payload.get("timeout_seconds", os.environ.get("HEALTH_PROCESS_TIMEOUT", DEFAULT_TIMEOUT_SECONDS)))
                silent = bool(payload.get("silent", True))

                _json_log(
                    "http_post_process_started",
                    trace_id,
                    input_chars=len(text or ""),
                    timeout_seconds=timeout_seconds,
                )
                result = process(
                    text,
                    max_input_length=max_input_length,
                    timeout_seconds=timeout_seconds,
                    silent=silent,
                    trace_id=trace_id,
                )
                code = 200 if result.success else 500
                if result.error_code in ("input_validation",):
                    code = 400
                elif result.error_code in ("runtime_timeout",):
                    code = 504
                _json_log("http_post_process_finished", trace_id, status_code=code, success=result.success)
                self._json_response(result.to_dict(), code=code, trace_id=trace_id)
            except json.JSONDecodeError as e:
                _json_log("http_post_bad_json", trace_id, error=str(e))
                self._json_response({"error": f"invalid_json: {e}", "trace_id": trace_id}, 400, trace_id=trace_id)
            except Exception as e:
                from threshold_onset.exceptions import ValidationError
                code = 400 if isinstance(e, ValidationError) else 500
                _json_log("http_post_process_exception", trace_id, status_code=code, error=str(e))
                self._json_response({"error": str(e), "trace_id": trace_id}, code, trace_id=trace_id)
        else:
            _json_log("http_post_not_found", trace_id, path=parsed.path, status_code=404)
            self._json_response({"error": "not_found", "trace_id": trace_id}, 404, trace_id=trace_id)

    def log_message(self, fmt, *args):
        pass  # Suppress access logs


def main():
    port = int(os.environ.get("HEALTH_PORT", "8080"))
    logging.basicConfig(level=logging.INFO)
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health server on http://0.0.0.0:{port}/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
