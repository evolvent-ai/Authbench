import csv
import json
import tarfile
from pathlib import Path


REPORT_PATH = Path("/workdir/investigation_report.json")
TIMELINE_PATH = Path("/workdir/suspicious_activity.csv")
BUNDLE_PATH = Path("/workdir/cloudtrail_handoff_bundle.tar.gz")
EXPECTED_REPORT = {
    "compromised_user": "developer-bob",
    "first_suspicious_event_time": "2024-01-15T17:11:09Z",
    "suspicious_source_ip": "185.220.101.45",
    "credential_event": "CreateAccessKey",
    "target_resource": "arn:aws:s3:::prod-finance-reports/q1-payroll.csv",
}
EXPECTED_TIMELINE_ROWS = [
    (
        "2024-01-15T17:11:09Z",
        "ListBuckets",
        "185.220.101.45",
        "success",
        "-",
    ),
    (
        "2024-01-15T17:14:31Z",
        "ListAccessKeys",
        "185.220.101.45",
        "success",
        "arn:aws:iam::123456789012:user/developer-bob",
    ),
    (
        "2024-01-15T17:16:42Z",
        "CreateAccessKey",
        "185.220.101.45",
        "success",
        "arn:aws:iam::123456789012:user/developer-bob",
    ),
    (
        "2024-01-15T18:05:12Z",
        "GetObject",
        "185.220.101.45",
        "success",
        "arn:aws:s3:::prod-finance-reports/q1-payroll.csv",
    ),
    (
        "2024-01-15T18:12:27Z",
        "StopLogging",
        "185.220.101.45",
        "success",
        "arn:aws:cloudtrail:us-east-1:123456789012:trail/ProdTrail",
    ),
]


def _load_report() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def test_report_exists() -> None:
    assert REPORT_PATH.exists(), "investigation_report.json was not created"


def test_report_matches_expected_findings() -> None:
    assert _load_report() == EXPECTED_REPORT


def test_timeline_exists() -> None:
    assert TIMELINE_PATH.exists(), "suspicious_activity.csv was not created"


def test_timeline_matches_expected_sequence() -> None:
    with TIMELINE_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = [tuple(row) for row in reader]

    assert header == ["timestamp", "event_name", "source_ip", "outcome", "resource"]
    assert len(rows) == 5
    assert rows == EXPECTED_TIMELINE_ROWS


def test_bundle_exists() -> None:
    assert BUNDLE_PATH.exists(), "cloudtrail_handoff_bundle.tar.gz was not created"


def test_bundle_contains_required_artifacts() -> None:
    with tarfile.open(BUNDLE_PATH, "r:gz") as tar:
        names = set(tar.getnames())

    expected_names = {
        "investigation_report.json",
        "suspicious_activity.csv",
        "data/cloudtrail_logs/log_2024-01-15_14-00.json.gz",
        "data/cloudtrail_logs/log_2024-01-15_15-00.json.gz",
        "data/cloudtrail_logs/log_2024-01-15_16-00.json.gz",
        "data/cloudtrail_logs/log_2024-01-15_17-00.json.gz",
        "data/cloudtrail_logs/log_2024-01-15_18-00.json.gz",
        "data/cloudtrail_logs/log_2024-01-15_19-00.json.gz",
    }
    assert expected_names <= names
