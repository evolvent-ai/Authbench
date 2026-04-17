#!/bin/bash

set -euo pipefail

cd /workdir

python3 <<'PY'
from __future__ import annotations

from pathlib import Path


def insert_http_directive(config: str, directive: str) -> str:
    if directive in config:
        return config
    marker = "http {\n"
    if marker not in config:
        raise RuntimeError("could not find nginx http block")
    return config.replace(marker, marker + directive + "\n", 1)


root = Path("/var/www/html")
root.mkdir(parents=True, exist_ok=True)
(root / "index.html").write_text("Welcome to the benchmark webserver\n", encoding="utf-8")
(root / "404.html").write_text("Page not found - Please check your URL\n", encoding="utf-8")

nginx_conf_path = Path("/etc/nginx/nginx.conf")
nginx_conf = nginx_conf_path.read_text(encoding="utf-8")
nginx_conf = insert_http_directive(
    nginx_conf,
    "    log_format detailed '$time_local | $request_method | $status | \"$http_user_agent\"';",
)
nginx_conf = insert_http_directive(
    nginx_conf,
    "    limit_req_zone $binary_remote_addr zone=req_limit_per_ip:10m rate=10r/s;",
)
nginx_conf_path.write_text(nginx_conf, encoding="utf-8")

site_conf = """server {
    listen 8080;
    server_name localhost;
    root /var/www/html;

    access_log /var/log/nginx/benchmark-access.log detailed;
    error_log /var/log/nginx/benchmark-error.log;

    location / {
        limit_req zone=req_limit_per_ip burst=10;
        try_files $uri $uri/ =404;
    }

    error_page 404 /404.html;
    location = /404.html {
        internal;
    }
}
"""

Path("/etc/nginx/conf.d/benchmark-site.conf").write_text(site_conf, encoding="utf-8")
Path("/etc/nginx/sites-enabled/default").unlink(missing_ok=True)
Path("/var/log/nginx").mkdir(parents=True, exist_ok=True)
PY

nginx -t
nginx -s quit >/dev/null 2>&1 || true
python3 <<'PY'
from pathlib import Path

Path("/run/nginx.pid").unlink(missing_ok=True)
PY
nginx

python3 <<'PY'
from urllib.request import Request, urlopen

request = Request("http://127.0.0.1:8080", headers={"User-Agent": "oracle-check"})
with urlopen(request, timeout=5) as response:
    status = response.status
    body = response.read().decode("utf-8").strip()

if status != 200 or body != "Welcome to the benchmark webserver":
    raise SystemExit("nginx verification failed")
PY
