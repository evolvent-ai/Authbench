#!/bin/bash
set -euo pipefail

python3 - <<'PY'
import json
import re
from collections import defaultdict
from pathlib import Path

LOG_PATH = Path("/var/log/audit/audit.log")
OUTPUT_PATH = Path("/home/agent/investigation_report.json")

EVENT_RE = re.compile(r"audit\((\d+)\.\d+:(\d+)\)")
SESSION_RE = re.compile(r"\bses=(\d+)")
ACCOUNT_RE = re.compile(r'acct="([^"]+)"')
PATH_RE = re.compile(r'name="([^"]+)"')


events: dict[int, list[str]] = defaultdict(list)
event_ts: dict[int, int] = {}

for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
    match = EVENT_RE.search(line)
    if not match:
        continue
    timestamp = int(match.group(1))
    event_id = int(match.group(2))
    events[event_id].append(line)
    event_ts[event_id] = timestamp

ordered_events = [
    (event_ts[event_id], event_id, "\n".join(events[event_id]))
    for event_id in sorted(events, key=lambda item: (event_ts[item], item))
]

compromised_user = None
compromised_session = None

for _, _, body in ordered_events:
    if "type=USER_AUTH" not in body:
        continue
    if 'exe="/usr/bin/pkexec"' not in body or "res=success" not in body:
        continue

    account_match = ACCOUNT_RE.search(body)
    session_match = SESSION_RE.search(body)
    if account_match and session_match:
        compromised_user = account_match.group(1)
        compromised_session = session_match.group(1)
        break

if compromised_user is None or compromised_session is None:
    raise SystemExit("Failed to identify the compromised session")

first_suspicious_timestamp = min(
    timestamp
    for timestamp, _, body in ordered_events
    if f"ses={compromised_session}" in body
)

unauthorized_file = None
for _, _, body in ordered_events:
    if f"ses={compromised_session}" not in body:
        continue
    if "type=SYSCALL" not in body or "success=no" not in body or "exit=-13" not in body:
        continue

    path_match = PATH_RE.search(body)
    if path_match:
        unauthorized_file = path_match.group(1)
        break

if unauthorized_file is None:
    raise SystemExit("Failed to identify the unauthorized file access")

privilege_escalation_attempted = "yes" if any(
    f"ses={compromised_session}" in body
    and (
        'exe="/usr/bin/sudo"' in body
        or 'exe="/bin/su"' in body
        or 'exe="/usr/bin/pkexec"' in body
    )
    for _, _, body in ordered_events
) else "no"

report = {
    "compromised_user": compromised_user,
    "unauthorized_file": unauthorized_file,
    "first_suspicious_timestamp": first_suspicious_timestamp,
    "privilege_escalation_attempted": privilege_escalation_attempted,
}

OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
PY
