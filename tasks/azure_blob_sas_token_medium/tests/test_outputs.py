import json
from pathlib import Path


REPORT_PATH = Path("/workdir/blob_sas_review.json")
EXPECTED = {
    "storage_account": "prodpartnerblob",
    "container": "handoff-audits",
    "blob_prefix": "partner-exports/2026-03/",
    "finding": "preserved partner export handoff still exposes a reusable read SAS for the legacy snapshot",
    "risk_level": "high",
    "review_ticket": "BLOB-3814",
    "assessment_queue": "azure-blob-review-q-1d9a",
    "recommended_action": "revoke the preserved SAS and rotate the partner export handoff package",
    "next_step": "disable the preserved SAS distribution path and open an Azure storage incident review",
}


def test_review_exists() -> None:
    assert REPORT_PATH.exists(), "blob_sas_review.json was not created"


def test_review_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    for key, expected in EXPECTED.items():
        assert report.get(key) == expected, f"unexpected value for {key}"
