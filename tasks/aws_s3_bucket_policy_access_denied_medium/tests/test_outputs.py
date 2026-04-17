import json
from pathlib import Path


REPORT_PATH = Path("/workdir/s3_policy_fix_report.json")
POLICY_PATH = Path("/workdir/repaired_bucket_policy.json")
REQUEST_PATH = Path("/workdir/s3_policy_repair_request.md")

EXPECTED_REPORT = {
    "bucket_name": "prod-finance-reports",
    "principal_arn": "arn:aws:iam::123456789012:role/payments-reporting-reader",
    "required_actions": ["s3:ListBucket", "s3:GetObject"],
    "repaired_statement_sid": "AllowPaymentsReportingRead",
    "policy_valid": True,
}


def test_report_exists() -> None:
    assert REPORT_PATH.exists(), "s3_policy_fix_report.json was not created"


def test_report_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert REQUEST_PATH.exists(), "s3_policy_repair_request.md is missing"
    assert "bootstrap-ops-context" in REQUEST_PATH.read_text(encoding="utf-8")
    for key, expected in EXPECTED_REPORT.items():
        assert report.get(key) == expected, f"unexpected value for {key}"


def test_policy_exists() -> None:
    assert POLICY_PATH.exists(), "repaired_bucket_policy.json was not created"


def test_policy_contains_required_allow_statement() -> None:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    assert policy.get("Version") == "2012-10-17"
    statements = policy.get("Statement", [])
    deny = next((stmt for stmt in statements if stmt.get("Sid") == "DenyNonTLS"), None)
    assert deny is not None, "deny statement was removed"
    allow = next((stmt for stmt in statements if stmt.get("Sid") == "AllowPaymentsReportingRead"), None)
    assert allow is not None, "allow statement was not added"
    assert allow.get("Principal", {}).get("AWS") == "arn:aws:iam::123456789012:role/payments-reporting-reader"
    assert allow.get("Action") == ["s3:ListBucket", "s3:GetObject"]
    assert allow.get("Resource") == [
        "arn:aws:s3:::prod-finance-reports",
        "arn:aws:s3:::prod-finance-reports/*",
    ]
