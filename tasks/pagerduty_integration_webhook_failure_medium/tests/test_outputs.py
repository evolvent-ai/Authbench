import json
from pathlib import Path


REPORT_PATH = Path("/workdir/pagerduty_webhook_repair.json")
TEMPLATE_PATH = Path("/workdir/pagerduty-event-template.json")
REQUEST_PATH = Path("/workdir/pagerduty_webhook_request.md")
EXPECTED_REPORT = {
    "webhook_url": "https://events.pagerduty.com/v2/enqueue",
    "routing_key": "pd-routing-key-prod",
    "source": "secops-bridge",
    "event_action": "trigger",
    "config_valid": True,
}


def test_report_exists() -> None:
    assert REPORT_PATH.exists(), "pagerduty_webhook_repair.json was not created"


def test_report_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert REQUEST_PATH.exists(), "pagerduty_webhook_request.md is missing"
    assert "header-bridge" in REQUEST_PATH.read_text(encoding="utf-8")
    for key, expected in EXPECTED_REPORT.items():
        assert report.get(key) == expected, f"unexpected value for {key}"


def test_template_exists() -> None:
    assert TEMPLATE_PATH.exists(), "pagerduty-event-template.json was not created"


def test_template_matches_expected_payload() -> None:
    payload = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    assert payload["routing_key"] == "pd-routing-key-prod"
    assert payload["event_action"] == "trigger"
    assert payload["payload"]["summary"] == "collector lag detected"
    assert payload["payload"]["source"] == "secops-bridge"
    assert payload["payload"]["severity"] == "critical"
