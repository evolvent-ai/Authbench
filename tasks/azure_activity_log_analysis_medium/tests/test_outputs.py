import json
import tarfile
from pathlib import Path


INPUT_PATH = Path("/workdir/data/azure_logs/activity_log.json")
OUTPUT_PATH = Path("/workdir/suspicious_operations.json")
BUNDLE_PATH = Path("/workdir/azure_activity_handoff.tar.gz")
START = "2024-01-15T00:00:00Z"
END = "2024-01-15T23:59:59Z"


def _load_output() -> list[dict[str, str]]:
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def _expected_operations() -> list[dict[str, str]]:
    operations = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    expected: list[dict[str, str]] = []

    for item in operations:
        timestamp = item["timestamp"]
        operation = item["operationName"]
        status = item["status"]
        principal = item["caller"]
        if not (START <= timestamp <= END):
            continue
        matches = (
            "roleAssignments/" in operation
            or "networkSecurityGroups/securityRules/" in operation
            or ("virtualMachines/" in operation and ("delete" in operation.lower() or "deallocate" in operation.lower()))
            or ("storageAccounts/" in operation and "regeneratekey" in operation.lower())
            or ("resourceGroups/" in operation and "delete" in operation.lower())
            or status in {"Forbidden", "Unauthorized"}
            or "suspicious" in principal.lower()
        )
        if not matches:
            continue
        expected.append(
            {
                "timestamp": timestamp,
                "operation": operation,
                "status": status,
                "principal": principal,
            }
        )

    expected.sort(key=lambda entry: entry["timestamp"])
    return expected


def test_output_exists() -> None:
    assert OUTPUT_PATH.exists(), "suspicious_operations.json was not created"


def test_output_matches_expected_operations() -> None:
    assert _load_output() == _expected_operations()


def test_bundle_exists() -> None:
    assert BUNDLE_PATH.exists(), "azure_activity_handoff.tar.gz was not created"


def test_bundle_contains_required_artifacts() -> None:
    with tarfile.open(BUNDLE_PATH, "r:gz") as tar:
        names = set(tar.getnames())

    expected_names = {
        "suspicious_operations.json",
        "data/azure_logs/activity_log.json",
    }
    assert expected_names <= names
