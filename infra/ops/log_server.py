#!/usr/bin/env python3
"""Minimal HTTP server that exposes iCLONE logs and ACP status to Flowise tools."""
import subprocess, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

LOG_PATH = Path.home() / "vegeta-autopilot.log"
ACP_BIN = "/opt/homebrew/bin/acp"
CHAIN_ID = "8453"
PORT = 7861

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def send_text(self, body: str, code=200):
        b = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/logs":
            try:
                lines = LOG_PATH.read_text().splitlines()
                self.send_text("\n".join(lines[-30:]))
            except Exception as e:
                self.send_text(f"Error: {e}", 500)

        elif self.path.startswith("/jobs"):
            limit = self.path.split("=")[-1] if "=" in self.path else "10"
            try:
                r = subprocess.run([ACP_BIN, "job", "history", "--chain-id", CHAIN_ID, "--limit", limit],
                                   capture_output=True, text=True, timeout=30)
                self.send_text(r.stdout or r.stderr or "No output")
            except Exception as e:
                self.send_text(f"Error: {e}", 500)

        elif self.path == "/status":
            try:
                r = subprocess.run([ACP_BIN, "agent", "whoami"], capture_output=True, text=True, timeout=15)
                log_tail = "\n".join(LOG_PATH.read_text().splitlines()[-10:]) if LOG_PATH.exists() else ""
                self.send_text(f"=== Agent ===\n{r.stdout}\n=== Last logs ===\n{log_tail}")
            except Exception as e:
                self.send_text(f"Error: {e}", 500)

        else:
            self.send_text("iCLONE Log Server\nEndpoints: /logs  /jobs?limit=10  /status")

if __name__ == "__main__":
    print(f"iCLONE log server running on http://localhost:{PORT}")
    HTTPServer(("localhost", PORT), Handler).serve_forever()
