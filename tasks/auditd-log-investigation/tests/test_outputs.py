import json
from pathlib import Path


REPORT_PATH = Path("/home/agent/investigation_report.json")


def load_report() -> dict:
    with REPORT_PATH.open(encoding="utf-8") as report_file:
        return json.load(report_file)


def test_report_file_exists():
    assert REPORT_PATH.exists(), f"{REPORT_PATH} does not exist"


def test_report_is_valid_json():
    data = load_report()
    assert isinstance(data, dict), "Report file must contain a JSON object"


def test_report_has_required_fields():
    data = load_report()
    expected_fields = {
        "compromised_user",
        "unauthorized_file",
        "first_suspicious_timestamp",
        "privilege_escalation_attempted",
    }
    assert set(data) == expected_fields, f"Report fields mismatch: {sorted(data)}"


def test_compromised_user_correct():
    data = load_report()
    assert data["compromised_user"] == "webadmin"


def test_unauthorized_file_correct():
    data = load_report()
    assert data["unauthorized_file"] == "/etc/shadow"


def test_first_suspicious_timestamp_correct():
    data = load_report()
    assert isinstance(data["first_suspicious_timestamp"], int)
    assert data["first_suspicious_timestamp"] == 1701242890


def test_privilege_escalation_attempted_correct():
    data = load_report()
    assert data["privilege_escalation_attempted"] in {"yes", "no"}
    assert data["privilege_escalation_attempted"] == "yes"
