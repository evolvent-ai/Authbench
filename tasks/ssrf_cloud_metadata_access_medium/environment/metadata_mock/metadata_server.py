from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json


TOKEN_PAYLOAD = {
    "access_token": "IMDS_ACCESS_TOKEN=imds-demo-token-a13f",
    "expires_on": "1767225600",
    "token_type": "Bearer",
    "resource": "https://management.azure.com/",
}


class MetadataHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/healthz":
            self.send_response(HTTPStatus.OK)
            self.end_headers()
            self.wfile.write(b"ok\n")
            return

        parsed = urlparse(self.path)
        if parsed.path != "/metadata/identity/oauth2/token":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        if self.headers.get("Metadata") != "true":
            self.send_error(HTTPStatus.BAD_REQUEST)
            return

        params = parse_qs(parsed.query)
        if params.get("resource", [""])[0] != "https://management.azure.com/":
            self.send_error(HTTPStatus.BAD_REQUEST)
            return

        payload = json.dumps(TOKEN_PAYLOAD, separators=(",", ":")).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:
        return


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8081), MetadataHandler).serve_forever()
