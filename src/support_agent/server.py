"""Lightweight HTTP server exposing POST /api/agent/message.

Uses Python standard library (ThreadingHTTPServer) with zero extra dependencies.
Proxied from Vite dev server via /api -> http://localhost:8000.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from support_agent.agent import get_support_agent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("support_agent_server")


class AgentHTTPRequestHandler(BaseHTTPRequestHandler):
    """Handles agent message requests with full CORS and JSON serialization."""

    def _set_cors_headers(self, status: int = 200, content_type: str = "application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/api/health", "/health"):
            self._set_cors_headers(200)
            self.wfile.write(json.dumps({"status": "healthy", "service": "support_agent"}).encode("utf-8"))
            return

        self._set_cors_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        if self.path in ("/api/agent/stream", "/agent/stream"):
            self._handle_stream_request()
            return

        if self.path not in ("/api/agent/message", "/agent/message"):
            self._set_cors_headers(404)
            self.wfile.write(json.dumps({"error": f"Endpoint not found: {self.path}"}).encode("utf-8"))
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._set_cors_headers(400)
                self.wfile.write(json.dumps({"error": "Empty request body"}).encode("utf-8"))
                return

            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))

            conversation_id = payload.get("conversation_id", f"conv_{int(os.times()[4] * 1000)}")
            messages = payload.get("messages") or payload.get("history") or []

            if not isinstance(messages, list):
                self._set_cors_headers(400)
                self.wfile.write(json.dumps({"error": "Field 'messages' must be a list"}).encode("utf-8"))
                return

            logger.info("Executing pipeline for conversation_id=%s, turns=%d", conversation_id, len(messages))
            agent = get_support_agent()
            response_data = agent.handle(conversation_id=conversation_id, messages=messages)

            response_bytes = json.dumps(response_data, indent=2).encode("utf-8")
            self._set_cors_headers(200)
            self.wfile.write(response_bytes)
            logger.info("Completed request for conversation_id=%s successfully", conversation_id)

        except json.JSONDecodeError as err:
            logger.error("JSON decode error: %s", err)
            self._set_cors_headers(400)
            self.wfile.write(json.dumps({"error": f"Invalid JSON payload: {err}"}).encode("utf-8"))

        except Exception as err:
            logger.exception("Unexpected server error: %s", err)
            self._set_cors_headers(500)
            self.wfile.write(json.dumps({"error": f"Agent processing failed: {str(err)}"}).encode("utf-8"))

    def _handle_stream_request(self):
        """Handle POST /api/agent/stream — emit Server-Sent Events as each pipeline stage finishes."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._set_cors_headers(400)
                self.wfile.write(json.dumps({"error": "Empty request body"}).encode("utf-8"))
                return

            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))

            conversation_id = payload.get("conversation_id", f"conv_{int(os.times()[4] * 1000)}")
            messages = payload.get("messages") or payload.get("history") or []

            if not isinstance(messages, list):
                self._set_cors_headers(400)
                self.wfile.write(json.dumps({"error": "Field 'messages' must be a list"}).encode("utf-8"))
                return

            # Send SSE headers — no Content-Length since we stream
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()

            logger.info("[STREAM] Starting pipeline for conversation_id=%s, turns=%d", conversation_id, len(messages))
            agent = get_support_agent()

            for event in agent.handle_stream(conversation_id=conversation_id, messages=messages):
                line = f"data: {json.dumps(event)}\n\n"
                self.wfile.write(line.encode("utf-8"))
                self.wfile.flush()

            # Signal end-of-stream
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            logger.info("[STREAM] Completed pipeline for conversation_id=%s", conversation_id)

        except json.JSONDecodeError as err:
            logger.error("[STREAM] JSON decode error: %s", err)
            try:
                error_line = f"data: {json.dumps({'type': 'error', 'error': str(err)})}\n\n"
                self.wfile.write(error_line.encode("utf-8"))
                self.wfile.flush()
            except Exception:
                pass

        except Exception as err:
            logger.exception("[STREAM] Unexpected error: %s", err)
            try:
                error_line = f"data: {json.dumps({'type': 'error', 'error': str(err)})}\n\n"
                self.wfile.write(error_line.encode("utf-8"))
                self.wfile.flush()
            except Exception:
                pass


def run_server(port: int = 8000, host: str = "0.0.0.0"):
    ThreadingHTTPServer.allow_reuse_address = True
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, AgentHTTPRequestHandler)
    logger.info("SupportAgent Live Server running on http://%s:%d", host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    run_server(port=port)
