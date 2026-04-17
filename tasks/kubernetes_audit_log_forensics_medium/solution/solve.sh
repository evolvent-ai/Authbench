#!/usr/bin/env bash
set -euo pipefail

/usr/bin/python3 - <<'PY'
import json
import tarfile
from pathlib import Path

NOTE_PATH = Path("/workdir/kubernetes_handoff_note.txt")
INPUT_PATH = Path("/workdir/data/kubernetes/audit.log")
OUTPUT_PATH = Path("/workdir/security_report.json")
BUNDLE_PATH = Path("/workdir/kubernetes_audit_handoff.tar.gz")

NOTE_PATH.read_text(encoding="utf-8")

failed_auth_count = 0
secret_access_attempts = 0
failed_by_user: dict[str, int] = {}
first_incident_time: str | None = None

for line in INPUT_PATH.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    entry = json.loads(line)
    timestamp = entry["timestamp"]
    user = entry["user"]
    resource = entry["resource"]
    response_status = entry["responseStatus"]

    if resource == "secrets":
        secret_access_attempts += 1

    if response_status in {401, 403}:
        failed_auth_count += 1
        failed_by_user[user] = failed_by_user.get(user, 0) + 1
        if first_incident_time is None or timestamp < first_incident_time:
            first_incident_time = timestamp

report = {
    "failed_auth_count": failed_auth_count,
    "secret_access_attempts": secret_access_attempts,
    "most_suspicious_user": max(failed_by_user, key=failed_by_user.get),
    "first_incident_time": first_incident_time,
}
OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

with tarfile.open(BUNDLE_PATH, "w:gz") as tar:
    tar.add(OUTPUT_PATH, arcname="security_report.json")
    tar.add(INPUT_PATH, arcname="data/kubernetes/audit.log")
PY
