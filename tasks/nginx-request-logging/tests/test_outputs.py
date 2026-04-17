import re
import subprocess
import time
from pathlib import Path
from urllib import error, request


SITE_CONFIG_PATH = Path("/etc/nginx/conf.d/benchmark-site.conf")
NGINX_CONFIG_PATH = Path("/etc/nginx/nginx.conf")
ACCESS_LOG_PATH = Path("/var/log/nginx/benchmark-access.log")


def combined_config_text() -> str:
    parts: list[str] = []
    if NGINX_CONFIG_PATH.exists():
        parts.append(NGINX_CONFIG_PATH.read_text(encoding="utf-8"))
    conf_dir = SITE_CONFIG_PATH.parent
    if conf_dir.exists():
        for conf_path in sorted(conf_dir.glob("*.conf")):
            parts.append(conf_path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def fetch(path: str, *, user_agent: str) -> tuple[int, str]:
    req = request.Request(
        f"http://127.0.0.1:8080{path}",
        headers={"User-Agent": user_agent},
    )
    try:
        with request.urlopen(req, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def test_nginx_installed() -> None:
    result = subprocess.run(["nginx", "-v"], capture_output=True, text=True)
    assert result.returncode == 0, "nginx is not installed"


def test_nginx_running_and_index_page() -> None:
    status, body = fetch("/", user_agent="AuthBenchVerifier/index")
    assert status == 200, "nginx is not serving localhost:8080"
    assert body.strip() == "Welcome to the benchmark webserver"


def test_custom_404_page() -> None:
    status, body = fetch("/does-not-exist", user_agent="AuthBenchVerifier/404")
    assert status == 404, "custom 404 status was not returned"
    assert body.strip() == "Page not found - Please check your URL"


def test_nginx_config_syntax() -> None:
    result = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_site_config_contains_required_settings() -> None:
    assert SITE_CONFIG_PATH.exists(), "benchmark site config is missing"
    site_content = SITE_CONFIG_PATH.read_text(encoding="utf-8")
    config_text = combined_config_text()

    site_patterns = [
        r"listen\s+8080;",
        r"root\s+/var/www/html;",
        r"limit_req\s+zone=req_limit_per_ip\s+burst=10;",
        r"error_page\s+404\s+/404\.html;",
    ]
    config_patterns = [
        r"access_log\s+/var/log/nginx/benchmark-access\.log\s+detailed;",
        r"error_log\s+/var/log/nginx/benchmark-error\.log\s*;",
    ]

    for pattern in site_patterns:
        assert re.search(pattern, site_content), f"missing site config pattern: {pattern}"
    for pattern in config_patterns:
        assert re.search(pattern, config_text), f"missing nginx config pattern: {pattern}"


def test_nginx_conf_contains_log_format_and_rate_limit_zone() -> None:
    config_text = combined_config_text()
    assert config_text, "no nginx config content found"
    assert re.search(
        r"log_format\s+detailed\s+'[^']*\$time_local[^']*\$request_method[^']*\$status[^']*\"\$http_user_agent\"[^']*';",
        config_text,
    ), "missing detailed log_format with time, method, status, and quoted user agent"
    assert re.search(
        r"limit_req_zone\s+\$binary_remote_addr\s+zone=req_limit_per_ip:10m\s+rate=10r/s;",
        config_text,
    ), "missing required limit_req_zone"


def test_default_site_disabled() -> None:
    assert not Path("/etc/nginx/sites-enabled/default").exists(), "default nginx site is still enabled"


def test_access_log_created_with_expected_format() -> None:
    user_agent = f"AuthBenchVerifier/{int(time.time())}"
    status, _ = fetch("/", user_agent=user_agent)
    assert status == 200

    time.sleep(1)
    assert ACCESS_LOG_PATH.exists(), "benchmark access log was not created"

    matching_lines = [
        line
        for line in ACCESS_LOG_PATH.read_text(encoding="utf-8").splitlines()
        if user_agent in line
    ]
    assert matching_lines, "could not find verifier request in access log"

    line = matching_lines[-1]
    timestamp_match = re.match(r"\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}\s[+-]\d{4}", line)
    assert timestamp_match, f"timestamp missing from log line: {line}"
    assert "GET" in line, f"request method missing in log line: {line}"
    quoted_user_agent = f"\"{user_agent}\""
    assert quoted_user_agent in line, f"user agent was not double-quoted: {line}"

    status_match = re.search(r"\b200\b", line)
    assert status_match, f"status code missing in log line: {line}"
    assert line.index("GET") < status_match.start() < line.index(quoted_user_agent), (
        f"log line did not keep method, status, and user agent in order: {line}"
    )
