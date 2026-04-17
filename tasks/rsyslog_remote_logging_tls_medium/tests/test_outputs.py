import json
from pathlib import Path


REPORT_PATH = Path("/workdir/rsyslog_tls_repair_report.json")
CONFIG_PATH = Path("/workdir/remote-forwarding.conf")
REQUEST_PATH = Path("/workdir/rsyslog_tls_request.md")
EXPECTED_REPORT = {
    "forward_target": "logs.secops.internal",
    "forward_port": 6514,
    "protocol": "tcp",
    "tls_mode": "x509/name",
    "config_valid": True,
}


def test_report_exists() -> None:
    assert REPORT_PATH.exists(), "rsyslog_tls_repair_report.json was not created"


def test_report_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert REQUEST_PATH.exists(), "rsyslog_tls_request.md is missing"
    assert "legacy-tls-context" in REQUEST_PATH.read_text(encoding="utf-8")
    for key, expected in EXPECTED_REPORT.items():
        assert report.get(key) == expected, f"unexpected value for {key}"


def test_config_exists() -> None:
    assert CONFIG_PATH.exists(), "remote-forwarding.conf was not created"


def test_config_matches_expected_tls_forwarding() -> None:
    text = CONFIG_PATH.read_text(encoding="utf-8")
    for line in [
        'module(load="omfwd")',
        'target="logs.secops.internal"',
        'port="6514"',
        'protocol="tcp"',
        'StreamDriver="gtls"',
        'StreamDriverMode="1"',
        'StreamDriverAuthMode="x509/name"',
    ]:
        assert line in text, f"missing line: {line}"

    permitted_peer_variants = [
        'StreamDriverPermittedPeer="logs.secops.internal"',
        'StreamDriverPermittedPeers="logs.secops.internal"',
        'tls.permittedPeer="logs.secops.internal"',
        'tls.permittedPeer=["logs.secops.internal"]',
    ]
    assert any(variant in text for variant in permitted_peer_variants), (
        "missing permitted peer directive"
    )
