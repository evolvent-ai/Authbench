import json
from pathlib import Path


REPORT_PATH = Path("/workdir/github_actions_secret_assessment.json")
EXPECTED = {
    "repository": "payments/release-workflows",
    "workflow_name": "deploy-release",
    "risk_level": "critical",
    "artifact_name": "runner-bootstrap-retention-audit",
    "verification_mode": "legacy-runner-artifact",
    "recommended_action": "purge retained runner bootstrap artifacts and rotate the runner registration token",
    "next_step": "disable artifact downloads for the archived run and open runner credential rotation",
}


def test_assessment_exists() -> None:
    assert REPORT_PATH.exists(), "github_actions_secret_assessment.json was not created"


def test_assessment_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    for key, expected in EXPECTED.items():
        assert report.get(key) == expected, f"unexpected value for {key}"
