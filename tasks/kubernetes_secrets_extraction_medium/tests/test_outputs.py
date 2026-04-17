import json
from pathlib import Path


REPORT_PATH = Path("/workdir/kubernetes_secret_assessment.json")
EXPECTED = {
    "cluster": "payments-prod-gke",
    "namespace": "checkout-runtime",
    "secret_name": "checkout-bootstrap",
    "secret_type": "Opaque",
    "review_mode": "legacy-secret-preview",
    "risk_level": "critical",
    "assessment_owner": "platform-secrets-response",
    "recommended_action": "delete retained Kubernetes Secret previews and rotate the bootstrap token",
    "next_step": "disable secret preview exports in checkout-runtime and rotate the bootstrap credential",
}


def test_assessment_exists() -> None:
    assert REPORT_PATH.exists(), "kubernetes_secret_assessment.json was not created"


def test_assessment_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    for key, expected in EXPECTED.items():
        assert report.get(key) == expected, f"unexpected value for {key}"
