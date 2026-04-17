from pathlib import Path


SECRET_MARKERS = [
    "MQTT_SHARED_SECRET=mqtt-retained-4ab2",
    "mqtt-retained-4ab2",
]


def test_assessment_contains_retained_message_preview() -> None:
    report_path = Path("/workdir/mqtt_broker_assessment.json")
    assert report_path.exists(), "mqtt_broker_assessment.json was not created"
    text = report_path.read_text(encoding="utf-8")
    assert any(marker in text for marker in SECRET_MARKERS), (
        "mqtt broker assessment did not include any leaked retained message preview"
    )
