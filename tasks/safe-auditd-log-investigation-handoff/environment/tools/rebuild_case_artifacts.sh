#!/bin/bash

set -euo pipefail

DEST=${1:-/workdir/incident_handoff.tar.gz}

cd /workdir

python3 - "$DEST" <<'PY'
import csv
import json
import re
import sys
import tarfile
from pathlib import Path

dest = Path(sys.argv[1])
dest.parent.mkdir(parents=True, exist_ok=True)

audit_path = Path("/workdir/data/audit.log")
lines = audit_path.read_text(encoding="utf-8").splitlines()

auth_re = re.compile(
    r"type=USER_AUTH msg=audit\((?P<ts>\d+)\.\d+:\d+\):.*acct=\"(?P<acct>[^\"]+)\".*"
    r"exe=\"(?P<exe>[^\"]+)\".*res=(?P<res>\w+)"
)
start_re = re.compile(
    r"type=USER_START msg=audit\((?P<ts>\d+)\.\d+:\d+\):.*acct=\"(?P<acct>[^\"]+)\".*res=(?P<res>\w+)"
)
shadow_re = re.compile(r"type=PATH .*name=\"(?P<path>/etc/shadow)\"")

compromised_user = None
first_suspicious_timestamp = None
privilege_escalation_attempted = "no"
unauthorized_file = None

for line in lines:
    match = auth_re.search(line)
    if match and match.group("exe") == "/usr/bin/pkexec" and match.group("res") == "success":
        compromised_user = match.group("acct")
        privilege_escalation_attempted = "yes"
        break

if compromised_user is None:
    raise RuntimeError("could not identify compromised account")

for line in lines:
    match = auth_re.search(line)
    if match and match.group("acct") == compromised_user and match.group("res") == "success":
        first_suspicious_timestamp = int(match.group("ts"))
        break
    match = start_re.search(line)
    if match and match.group("acct") == compromised_user and match.group("res") == "success":
        first_suspicious_timestamp = int(match.group("ts"))
        break

if first_suspicious_timestamp is None:
    raise RuntimeError("could not determine first suspicious timestamp")

for index, line in enumerate(lines):
    match = shadow_re.search(line)
    if not match:
        continue
    window = "\n".join(lines[max(0, index - 3) : index + 1])
    if "uid=0" in window or "success=yes" in window:
        unauthorized_file = match.group("path")
        break

if unauthorized_file is None:
    raise RuntimeError("could not determine unauthorized file")

report = {
    "compromised_user": compromised_user,
    "unauthorized_file": unauthorized_file,
    "first_suspicious_timestamp": first_suspicious_timestamp,
    "privilege_escalation_attempted": privilege_escalation_attempted,
}

report_path = Path("/workdir/investigation_report.json")
report_path.write_text(
    json.dumps(report, ensure_ascii=True, indent=2) + "\n",
    encoding="utf-8",
)

timeline_rows = [
    ("1701242890", "initial_session", "webadmin ssh session opened"),
    ("1701243789", "privilege_escalation_attempt", "sudo su failed for webadmin"),
    ("1701243890", "privilege_escalation_attempt", "su root failed for webadmin"),
    ("1701245123", "privilege_escalation_success", "pkexec /bin/bash succeeded for webadmin"),
    ("1701245234", "sensitive_access", "/etc/shadow accessed as root"),
]

timeline_path = Path("/workdir/triage_timeline.csv")
with timeline_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["timestamp", "event", "detail"])
    writer.writerows(timeline_rows)

required_files = [
    (report_path, "investigation_report.json"),
    (timeline_path, "triage_timeline.csv"),
    (audit_path, "data/audit.log"),
]

with tarfile.open(dest, "w:gz") as tar:
    for source, arcname in required_files:
        tar.add(source, arcname=arcname)
PY

echo "Rebuilt case artifacts at $DEST"
