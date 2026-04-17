from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import time


UPLOAD_DIR = Path("/var/uploads")


class UploadHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/healthz":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        self.wfile.write(b"ok\n")

    def do_POST(self) -> None:
        if self.path != "/upload/oauth-review":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(content_length)
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        destination = UPLOAD_DIR / f"oauth-review-{time.time_ns()}.tar.gz"
        destination.write_bytes(payload)
        self.send_response(HTTPStatus.CREATED)
        self.end_headers()
        self.wfile.write(destination.name.encode("utf-8") + b"\n")

    def log_message(self, format: str, *args) -> None:
        return


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), UploadHandler).serve_forever()
