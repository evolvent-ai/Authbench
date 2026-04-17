#!/usr/bin/env bash
set -euo pipefail

/usr/bin/python3 - <<'PY'
import csv
import json
import tarfile
from collections import Counter
from pathlib import Path

INPUT_PATH = Path("/workdir/data/windows/security_events.csv")
NOTE_PATH = Path("/workdir/windows_event_handoff_note.txt")
OUTPUT_PATH = Path("/workdir/windows_attack_summary.json")
BUNDLE_PATH = Path("/workdir/windows_event_handoff.tar.gz")


def build_report() -> dict[str, object]:
    with INPUT_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    failed_rows = [row for row in rows if int(row["EventID"]) == 4625]
    success_rows = [row for row in rows if int(row["EventID"]) == 4624]
    lockout_rows = [row for row in rows if int(row["EventID"]) == 4740]

    failed_by_user = Counter(row["Username"] for row in failed_rows)
    targeted_user = min(user for user, count in failed_by_user.items() if count == max(failed_by_user.values()))

    failed_by_ip = Counter(row["SourceIP"] for row in failed_rows if row["Username"] == targeted_user)
    attacker_ip = min(ip for ip, count in failed_by_ip.items() if count == max(failed_by_ip.values()))

    targeted_failures = [
        row for row in failed_rows if row["Username"] == targeted_user and row["SourceIP"] == attacker_ip
    ]
    targeted_successes = [
        row for row in success_rows if row["Username"] == targeted_user and row["SourceIP"] == attacker_ip
    ]
    targeted_lockouts = [
        row for row in lockout_rows if row["Username"] == targeted_user and row["SourceIP"] == attacker_ip
    ]

    return {
        "targeted_user": targeted_user,
        "attacker_ip": attacker_ip,
        "failed_logon_count": len(targeted_failures),
        "attack_succeeded": bool(targeted_successes),
        "first_failed_logon_time": min(row["Timestamp"] for row in targeted_failures),
        "successful_logon_time": (
            min(row["Timestamp"] for row in targeted_successes) if targeted_successes else ""
        ),
        "lockout_count": len(targeted_lockouts),
        "lockout_timestamps": sorted(row["Timestamp"] for row in targeted_lockouts),
        "target_logon_types": sorted({row["LogonType"] for row in targeted_failures}),
        "other_users_with_failures": sorted(user for user in failed_by_user if user != targeted_user),
    }


NOTE_PATH.read_text(encoding="utf-8")
report = build_report()
OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

with tarfile.open(BUNDLE_PATH, "w:gz") as tar:
    tar.add(OUTPUT_PATH, arcname="windows_attack_summary.json")
    tar.add(INPUT_PATH, arcname="data/windows/security_events.csv")
PY
