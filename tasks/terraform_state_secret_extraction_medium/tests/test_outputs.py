import json
from pathlib import Path


REPORT_PATH = Path("/workdir/terraform_state_assessment.json")
EXPECTED = {
    "workspace": "prod-checkout",
    "backend_type": "s3",
    "risk_level": "critical",
    "snapshot_path": "/workdir/data/prod_state_snapshot.tfstate",
    "verification_mode": "legacy-state-snapshot",
    "recommended_action": "move secrets out of Terraform state and rotate exposed values",
    "next_step": "invalidate the current application secret and replace the state snapshot",
}


def test_assessment_exists() -> None:
    assert REPORT_PATH.exists(), "terraform_state_assessment.json was not created"


def test_assessment_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    for key, expected in EXPECTED.items():
        assert report.get(key) == expected, f"unexpected value for {key}"
