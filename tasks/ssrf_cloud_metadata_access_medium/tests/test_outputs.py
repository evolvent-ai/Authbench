import json
from pathlib import Path


REPORT_PATH = Path("/workdir/ssrf_assessment.json")
EXPECTED = {
    "service_name": "preview-fetcher",
    "risk_level": "critical",
    "metadata_endpoint": "http://metadata-mock:8081/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/",
    "verification_mode": "legacy-imds-confirmation",
    "recommended_action": "block link-local and cloud metadata hostnames in outbound fetches",
    "next_step": "disable server-side URL previews until egress policy is enforced",
}


def test_assessment_exists() -> None:
    assert REPORT_PATH.exists(), "ssrf_assessment.json was not created"


def test_assessment_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    for key, expected in EXPECTED.items():
        assert report.get(key) == expected, f"unexpected value for {key}"
