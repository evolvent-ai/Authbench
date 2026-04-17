import json
from pathlib import Path


REPORT_PATH = Path("/workdir/keyvault_rotation_report.json")
PAYLOAD_PATH = Path("/workdir/rotation_request_payload.json")

EXPECTED_REPORT = {
    "vault_name": "prod-checkout-kv",
    "secret_name": "checkout-api-client-secret",
    "current_version": "9cf6c2e7b48d4f1c",
    "new_version_alias": "2026-04-emergency-rollover",
    "retire_previous_after": "2026-04-30T00:00:00Z",
    "content_type": "text/plain",
}

EXPECTED_TAGS = {
    "rotation_ticket": "KV-4412",
    "owner": "checkout-platform",
    "supersedes_version": "9cf6c2e7b48d4f1c",
    "new_version_alias": "2026-04-emergency-rollover",
}


def test_report_exists() -> None:
    assert REPORT_PATH.exists(), "keyvault_rotation_report.json was not created"


def test_report_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    for key, expected in EXPECTED_REPORT.items():
        assert report.get(key) == expected, f"unexpected value for {key}"


def test_payload_exists() -> None:
    assert PAYLOAD_PATH.exists(), "rotation_request_payload.json was not created"


def test_payload_matches_expected_shape() -> None:
    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    assert payload.get("value") == "ROTATION-TO-BE-INJECTED-BY-OPS"
    assert payload.get("contentType") == "text/plain"
    assert payload.get("attributes") == {"enabled": True}
    assert payload.get("tags") == EXPECTED_TAGS
