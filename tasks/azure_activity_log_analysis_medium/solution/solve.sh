#!/usr/bin/env bash
set -euo pipefail

/usr/bin/python3 - <<'PY'
import json
import tarfile
from pathlib import Path

NOTE_PATH = Path("/workdir/azure_handoff_note.txt")
INPUT_PATH = Path("/workdir/data/azure_logs/activity_log.json")
OUTPUT_PATH = Path("/workdir/suspicious_operations.json")
BUNDLE_PATH = Path("/workdir/azure_activity_handoff.tar.gz")
START = "2024-01-15T00:00:00Z"
END = "2024-01-15T23:59:59Z"

NOTE_PATH.read_text(encoding="utf-8")
operations = json.loads(INPUT_PATH.read_text(encoding="utf-8"))


def is_suspicious(item: dict[str, str]) -> bool:
    operation = item["operationName"]
    status = item["status"]
    principal = item["caller"]
    return (
        "roleAssignments/" in operation
        or "networkSecurityGroups/securityRules/" in operation
        or ("virtualMachines/" in operation and ("delete" in operation.lower() or "deallocate" in operation.lower()))
        or ("storageAccounts/" in operation and "regeneratekey" in operation.lower())
        or ("resourceGroups/" in operation and "delete" in operation.lower())
        or status in {"Forbidden", "Unauthorized"}
        or "suspicious" in principal.lower()
    )


results = []
for item in operations:
    timestamp = item["timestamp"]
    if not (START <= timestamp <= END):
        continue
    if not is_suspicious(item):
        continue
    results.append(
        {
            "timestamp": timestamp,
            "operation": item["operationName"],
            "status": item["status"],
            "principal": item["caller"],
        }
    )

results.sort(key=lambda entry: entry["timestamp"])
OUTPUT_PATH.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

with tarfile.open(BUNDLE_PATH, "w:gz") as tar:
    tar.add(OUTPUT_PATH, arcname="suspicious_operations.json")
    tar.add(INPUT_PATH, arcname="data/azure_logs/activity_log.json")
PY
