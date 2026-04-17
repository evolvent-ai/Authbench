from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse


UPLOAD_DIR = Path("/var/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class UploadHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/upload/"):
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(content_length)
        upload_name = parsed.path.removeprefix("/upload/").strip("/") or "upload"
        destination = UPLOAD_DIR / f"{upload_name}.tar.gz"
        destination.write_bytes(payload)

        self.send_response(201)
        self.end_headers()
        self.wfile.write(b"created")

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), UploadHandler)
    server.serve_forever()
