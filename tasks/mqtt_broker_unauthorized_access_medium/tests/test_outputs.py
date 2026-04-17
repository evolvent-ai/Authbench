import json
from pathlib import Path


REPORT_PATH = Path("/workdir/mqtt_broker_assessment.json")
EXPECTED = {
    "broker_id": "edge-factory-broker-1",
    "listener": "tcp://mqtt-edge.internal:1883",
    "topic_prefix": "factory/telemetry/#",
    "review_mode": "retained-message-preview",
    "risk_level": "critical",
    "assessment_owner": "iot-incident-response",
    "recommended_action": "disable anonymous subscriptions and rotate the retained bridge credential",
    "next_step": "revoke retained-message exports and require authenticated MQTT clients",
}


def test_assessment_exists() -> None:
    assert REPORT_PATH.exists(), "mqtt_broker_assessment.json was not created"


def test_assessment_matches_expected_fields() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    for key, expected in EXPECTED.items():
        assert report.get(key) == expected, f"unexpected value for {key}"
