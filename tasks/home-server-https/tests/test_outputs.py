import os
import re
import socket
import subprocess
import urllib.request
from pathlib import Path


DOMAIN = "homeserver.local"
HTML_PATH = Path("/var/www/html/index.html")
DDCLIENT_PATH = Path("/etc/ddclient.conf")
CONFIG_PATHS = [
    Path("/etc/nginx/sites-available/default"),
    Path("/etc/nginx/sites-enabled/default"),
    Path("/etc/nginx/nginx.conf"),
]


def run(command: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["NO_PROXY"] = ",".join({
        "127.0.0.1",
        "localhost",
        DOMAIN,
        "google-api-mock",
    })
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        env=env,
    )


def get_ssl_config_text() -> str:
    for path in CONFIG_PATHS:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if "ssl_certificate" in content and DOMAIN in content:
                return content
    raise AssertionError("Could not find nginx SSL config for homeserver.local")


def get_certificate_paths() -> tuple[Path, Path]:
    config = get_ssl_config_text()
    cert_match = re.search(r"^\s*ssl_certificate\s+(\S+);", config, re.MULTILINE)
    key_match = re.search(r"^\s*ssl_certificate_key\s+(\S+);", config, re.MULTILINE)
    assert cert_match is not None, "nginx config missing ssl_certificate"
    assert key_match is not None, "nginx config missing ssl_certificate_key"
    return Path(cert_match.group(1)), Path(key_match.group(1))


def test_html_page_exists() -> None:
    assert HTML_PATH.exists(), f"Missing {HTML_PATH}"
    content = HTML_PATH.read_text(encoding="utf-8")
    assert "Welcome to My Home Server!" in content


def test_ddclient_configured() -> None:
    assert DDCLIENT_PATH.exists(), f"Missing {DDCLIENT_PATH}"
    content = DDCLIENT_PATH.read_text(encoding="utf-8")
    assert "homeserver.local" in content
    assert "protocol=googledomains" in content


def test_nginx_config_has_ssl() -> None:
    config = get_ssl_config_text()
    assert "listen 443 ssl" in config
    assert DOMAIN in config


def test_ssl_files_exist() -> None:
    cert_path, key_path = get_certificate_paths()
    assert cert_path.exists(), f"Missing certificate {cert_path}"
    assert key_path.exists(), f"Missing key {key_path}"


def test_certificate_valid_for_domain() -> None:
    cert_path, _ = get_certificate_paths()
    result = run(["openssl", "x509", "-in", str(cert_path), "-text", "-noout"])
    assert result.returncode == 0, result.stderr
    assert "DNS:homeserver.local" in result.stdout


def test_nginx_is_running() -> None:
    result = run(["pgrep", "-x", "nginx"])
    assert result.returncode == 0, "nginx is not running"


def test_port_443_is_listening() -> None:
    result = run(["netstat", "-ln"])
    assert result.returncode == 0, result.stderr
    assert ":443" in result.stdout, "Nothing is listening on port 443"


def test_dns_resolution() -> None:
    ip = socket.gethostbyname(DOMAIN)
    assert ip in {"172.20.0.30", "127.0.0.1"}, f"Unexpected IP: {ip}"


def test_https_returns_200() -> None:
    result = run([
        "curl",
        "-k",
        "-s",
        "-o",
        "/dev/null",
        "-w",
        "%{http_code}",
        f"https://{DOMAIN}",
    ])
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "200"


def test_https_content() -> None:
    result = run(["curl", "-k", "-s", f"https://{DOMAIN}"])
    assert result.returncode == 0, result.stderr
    assert "Welcome to My Home Server!" in result.stdout


def test_mock_api_accessible() -> None:
    with urllib.request.urlopen("http://google-api-mock:8080/health", timeout=10) as response:
        assert response.status == 200
        assert response.read().decode("utf-8") == '{"status":"ok"}'
