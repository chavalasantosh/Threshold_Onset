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
import sys
from pathlib import Path

# Ensure project root in path
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


def get_health_status():
    """Return health status dict."""
    try:
        from threshold_onset.config import get_config
        from threshold_onset import __version__
        get_config()
        return {"status": "ok", "version": __version__, "config_loaded": True}
    except Exception as e:
        return {"status": "degraded", "error": str(e), "config_loaded": False}


class HealthHandler(BaseHTTPRequestHandler):
    """Handle /health, /ready, and POST /process."""

    def _json_response(self, data, code=200):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/health", "/ready", "/"):
            status = get_health_status()
            code = 200 if status.get("status") == "ok" else 503
            self._json_response(status, code)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/process":
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(content_len).decode("utf-8")
                payload = json.loads(raw) if raw else {}
                text = payload.get("text", "")
                from threshold_onset.api import process
                result = process(text, silent=True)
                self._json_response(result.to_dict())
            except json.JSONDecodeError as e:
                self._json_response({"error": f"Invalid JSON: {e}"}, 400)
            except Exception as e:
                from threshold_onset.exceptions import ValidationError
                code = 400 if isinstance(e, ValidationError) else 500
                self._json_response({"error": str(e)}, code)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress access logs


def main():
    port = int(os.environ.get("HEALTH_PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health server on http://0.0.0.0:{port}/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
