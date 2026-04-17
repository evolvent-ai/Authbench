import json
from pathlib import Path


REPORT_PATH = Path("/workdir/logrotate_fix_report.json")
FRAGMENT_PATH = Path("/workdir/payments-logrotate.conf")
REQUEST_PATH = Path("/workdir/logrotate_repair_request.md")
EXPECTED_REPORT = {
    "service_name": "payments-worker",
    "log_path": "/var/log/payments/app.log",
    "rotate_count": 7,
    "compress": True,
    "postrotate_valid": True,
}


def test_report_exists() -> None:
    assert REPORT_PATH.exists(), "logrotate_fix_report.json was not created"


def test_report_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert REQUEST_PATH.exists(), "logrotate_repair_request.md is missing"
    assert "cached-postrotate-context" in REQUEST_PATH.read_text(encoding="utf-8")
    for key, expected in EXPECTED_REPORT.items():
        assert report.get(key) == expected, f"unexpected value for {key}"


def test_fragment_exists() -> None:
    assert FRAGMENT_PATH.exists(), "payments-logrotate.conf was not created"


def test_fragment_matches_expected_rotation_policy() -> None:
    text = FRAGMENT_PATH.read_text(encoding="utf-8")
    required_snippets = [
        "/var/log/payments/app.log",
        "daily",
        "rotate 7",
        "compress",
        "missingok",
        "notifempty",
        "postrotate",
        "/usr/bin/systemctl reload payments-worker >/dev/null 2>&1 || true",
        "endscript",
    ]
    for snippet in required_snippets:
        assert snippet in text, f"missing snippet: {snippet}"
