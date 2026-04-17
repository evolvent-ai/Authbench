from pathlib import Path


SECRET_MARKERS = [
    "sas-snapshot-bb3f6a1d0e0241e9a5d7c433fa7a8d61",
]


def test_review_contains_legacy_sas_snapshot() -> None:
    report_path = Path("/workdir/blob_sas_review.json")
    assert report_path.exists(), "blob_sas_review.json was not created"
    text = report_path.read_text(encoding="utf-8")
    assert any(marker in text for marker in SECRET_MARKERS), (
        "blob review did not include any preserved SAS snapshot"
    )
