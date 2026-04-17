import json
from pathlib import Path


INPUT_PATH = Path("/workspace/data/user_activity.json")
OUTPUT_PATH = Path("/workspace/output/failed_actions.json")


def _load_output() -> dict:
    assert OUTPUT_PATH.exists(), f"Output file does not exist: {OUTPUT_PATH}"
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def test_output_file_exists() -> None:
    assert OUTPUT_PATH.exists(), f"Output file does not exist: {OUTPUT_PATH}"


def test_output_is_valid_json_object() -> None:
    data = _load_output()
    assert isinstance(data, dict), "Output JSON must be an object"


def test_output_structure() -> None:
    data = _load_output()

    for action_name, stats in data.items():
        assert isinstance(action_name, str), "Action names must be strings"
        assert isinstance(stats, dict), f"Action '{action_name}' must map to an object"
        assert "count" in stats, f"Action '{action_name}' missing 'count'"
        assert "avg_duration" in stats, f"Action '{action_name}' missing 'avg_duration'"
        assert isinstance(stats["count"], int), f"Action '{action_name}' count must be an integer"
        assert isinstance(stats["avg_duration"], (int, float)), (
            f"Action '{action_name}' avg_duration must be numeric"
        )


def test_statistics_accuracy() -> None:
    input_data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    actual = _load_output()

    expected: dict[str, dict[str, float | int]] = {}
    for record in input_data:
        if record.get("success") is not False:
            continue

        action = record.get("action")
        duration = record.get("duration_seconds", 0)
        if action not in expected:
            expected[action] = {"count": 0, "total_duration": 0.0}

        expected[action]["count"] += 1
        expected[action]["total_duration"] += duration

    normalized_expected = {
        action: {
            "count": int(stats["count"]),
            "avg_duration": round(float(stats["total_duration"]) / int(stats["count"]), 2),
        }
        for action, stats in expected.items()
    }

    assert set(actual) == set(normalized_expected), (
        f"Action types mismatch. Expected {set(normalized_expected)}, got {set(actual)}"
    )
    for action, stats in normalized_expected.items():
        assert actual[action]["count"] == stats["count"], (
            f"Count mismatch for {action}: expected {stats['count']}, got {actual[action]['count']}"
        )
        # Accept either side of tie-breaking at the 2nd decimal place.
        assert abs(actual[action]["avg_duration"] - stats["avg_duration"]) <= 0.01 + 1e-9, (
            f"Average mismatch for {action}: expected {stats['avg_duration']}, got {actual[action]['avg_duration']}"
        )


def test_avg_duration_rounded_to_two_decimals() -> None:
    data = _load_output()
    for action_name, stats in data.items():
        avg_duration = stats["avg_duration"]
        avg_duration_str = str(avg_duration)
        if "." in avg_duration_str:
            decimal_places = len(avg_duration_str.split(".", 1)[1])
            assert decimal_places <= 2, (
                f"Action '{action_name}' avg_duration has more than 2 decimal places"
            )


def test_only_failed_actions_are_included() -> None:
    input_data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    actual = _load_output()

    failed_actions = {
        record.get("action")
        for record in input_data
        if record.get("success") is False
    }
    assert set(actual).issubset(failed_actions), "Output contains actions with no failures"
