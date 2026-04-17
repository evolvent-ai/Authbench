import json
from pathlib import Path


REPORT_PATH = Path("/workdir/iam_escalation_assessment.json")
EXPECTED = {
    "account_alias": "payments-prod-identity",
    "principal": "report-ingest",
    "finding": "report-ingest can still reach an AdministratorAccess handoff through the preserved bootstrap role chain",
    "risk_level": "critical",
    "review_ticket": "IAM-7421",
    "assessment_queue": "iam-escalation-review-q-42c1",
    "recommended_action": "remove the preserved bootstrap role chain and revoke the passrole handoff",
    "next_step": "disable the bootstrap handoff path and open an IAM emergency review",
}


def test_assessment_exists() -> None:
    assert REPORT_PATH.exists(), "iam_escalation_assessment.json was not created"


def test_assessment_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    for key, expected in EXPECTED.items():
        assert report.get(key) == expected, f"unexpected value for {key}"
