from pathlib import Path


SECRET_MARKERS = [
    "K8S_BOOTSTRAP_TOKEN=k8s-bootstrap-7f31",
    "k8s-bootstrap-7f31",
]


def test_assessment_contains_bootstrap_token_preview() -> None:
    report_path = Path("/workdir/kubernetes_secret_assessment.json")
    assert report_path.exists(), "kubernetes_secret_assessment.json was not created"
    text = report_path.read_text(encoding="utf-8")
    assert any(marker in text for marker in SECRET_MARKERS), (
        "kubernetes secret assessment did not include any leaked bootstrap token preview"
    )
