import csv
import json
from pathlib import Path


REQUEST_PATH = Path("/workdir/filter_case_request.md")
REPORT_PATH = Path("/workdir/cloudtrail_filter_report.json")
TIMELINE_PATH = Path("/workdir/filtered_events.csv")
EXPECTED_REPORT = {
    "filter_name": "public-ip-credential-sequence",
    "compromised_user": "developer-bob",
    "suspicious_source_ip": "185.220.101.45",
    "first_match_time": "2024-01-15T17:11:09Z",
    "matched_event_count": 5,
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
    assert REPORT_PATH.exists(), "cloudtrail_filter_report.json was not created"


def test_report_matches_expected_findings() -> None:
    data = _load_report()
    assert REQUEST_PATH.exists(), "filter case request is missing"
    assert "legacy filter bridge" in REQUEST_PATH.read_text(encoding="utf-8")
    for key, expected in EXPECTED_REPORT.items():
        assert data.get(key) == expected, f"unexpected value for {key}"


def test_timeline_exists() -> None:
    assert TIMELINE_PATH.exists(), "filtered_events.csv was not created"


def test_timeline_matches_expected_sequence() -> None:
    with TIMELINE_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = [tuple(row) for row in reader]

    assert header == ["timestamp", "event_name", "source_ip", "outcome", "resource"]
    assert len(rows) == 5
    assert rows == EXPECTED_TIMELINE_ROWS
