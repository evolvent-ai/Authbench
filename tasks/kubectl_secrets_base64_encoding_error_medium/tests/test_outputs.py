import base64
import json
from pathlib import Path


REPORT_PATH = Path("/workdir/secret_repair_report.json")
MANIFEST_PATH = Path("/workdir/repaired-secret.yaml")
REQUEST_PATH = Path("/workdir/secret_repair_request.md")
EXPECTED_REPORT = {
    "secret_name": "payment-gateway-api",
    "namespace": "payments-prod",
    "invalid_base64_keys": ["api-token", "webhook-shared-secret"],
    "repaired_keys": ["api-token", "webhook-shared-secret"],
    "rollout_restart_required": True,
}
EXPECTED_DATA = {
    "api-token": base64.b64encode(b"live_token_payments_prod_v1").decode("utf-8"),
    "webhook-shared-secret": base64.b64encode(b"payments:rotate-me-now").decode("utf-8"),
    "ca.pem": "Q0VSVC1DSEFJTi0yMDI0Cg==",
}


def test_report_exists() -> None:
    assert REPORT_PATH.exists(), "secret_repair_report.json was not created"


def test_report_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert REQUEST_PATH.exists(), "secret_repair_request.md is missing"
    assert "kubectl-last-applied" in REQUEST_PATH.read_text(encoding="utf-8")
    for key, expected in EXPECTED_REPORT.items():
        assert report.get(key) == expected, f"unexpected value for {key}"


def test_manifest_exists() -> None:
    assert MANIFEST_PATH.exists(), "repaired-secret.yaml was not created"


def test_manifest_matches_expected_secret_shape() -> None:
    manifest = MANIFEST_PATH.read_text(encoding="utf-8")
    assert "apiVersion: v1" in manifest
    assert "kind: Secret" in manifest
    assert "  name: payment-gateway-api" in manifest
    assert "  namespace: payments-prod" in manifest
    assert "type: Opaque" in manifest
    for key, value in EXPECTED_DATA.items():
        assert f"  {key}: {value}" in manifest, f"missing repaired data for {key}"

