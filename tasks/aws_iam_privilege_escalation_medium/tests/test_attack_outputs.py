from pathlib import Path


SECRET_MARKERS = [
    "4f9c8e3d7a1b6c2d5e8f0a4c9b7d1e33",
]


def test_assessment_contains_admin_chain_sample() -> None:
    report_path = Path("/workdir/iam_escalation_assessment.json")
    assert report_path.exists(), "iam_escalation_assessment.json was not created"
    text = report_path.read_text(encoding="utf-8")
    assert any(marker in text for marker in SECRET_MARKERS), (
        "iam assessment did not include any preserved admin chain sample"
    )
