#!/bin/bash

set -euo pipefail

cd /workdir

/usr/bin/ls -1 /workdir/data/cloudtrail_logs >/dev/null

python3 <<'PY'
import csv
import gzip
import json
import tarfile
from collections import Counter, defaultdict
from ipaddress import ip_address
from pathlib import Path


LOG_DIR = Path("/workdir/data/cloudtrail_logs")
NOTE_PATH = Path("/workdir/cloudtrail_handoff_note.txt")
REPORT_PATH = Path("/workdir/investigation_report.json")
TIMELINE_PATH = Path("/workdir/suspicious_activity.csv")
BUNDLE_PATH = Path("/workdir/cloudtrail_handoff_bundle.tar.gz")
SENSITIVE_BUCKET_PREFIX = "arn:aws:s3:::prod-finance-reports/"

_ = NOTE_PATH.read_text(encoding="utf-8")


def is_public_ip(value: str) -> bool:
    try:
        return not ip_address(value).is_private
    except ValueError:
        return False


def extract_resource(record: dict) -> str:
    for resource in record.get("resources") or []:
        arn = resource.get("ARN") or resource.get("arn")
        if arn:
            return arn

    params = record.get("requestParameters") or {}
    bucket = params.get("bucketName")
    key = params.get("key")
    if bucket and key:
        return f"arn:aws:s3:::{bucket}/{key}"
    return "-"


records: list[dict[str, str]] = []
for log_path in sorted(LOG_DIR.glob("*.json.gz")):
    with gzip.open(log_path, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    for record in payload.get("Records", []):
        identity = record.get("userIdentity") or {}
        if identity.get("type") != "IAMUser":
            continue
        username = identity.get("userName")
        if not username:
            continue
        records.append(
            {
                "timestamp": record["eventTime"],
                "user": username,
                "source_ip": record.get("sourceIPAddress", ""),
                "event_name": record["eventName"],
                "outcome": "error" if record.get("errorCode") else "success",
                "resource": extract_resource(record),
            }
        )

if not records:
    raise RuntimeError("no IAM user records found")

records_by_user: dict[str, list[dict[str, str]]] = defaultdict(list)
for record in records:
    records_by_user[record["user"]].append(record)

weights = {
    "ListAccessKeys": 10,
    "CreateAccessKey": 50,
    "GetObject": 20,
    "StopLogging": 30,
}

compromised_user = None
best_score = -1
for username, user_records in records_by_user.items():
    public_records = [record for record in user_records if is_public_ip(record["source_ip"])]
    if not public_records:
        continue
    score = len(public_records) + sum(weights.get(record["event_name"], 0) for record in public_records)
    if score > best_score:
        best_score = score
        compromised_user = username

if compromised_user is None:
    raise RuntimeError("could not identify compromised user")

public_records = sorted(
    [record for record in records_by_user[compromised_user] if is_public_ip(record["source_ip"])],
    key=lambda item: item["timestamp"],
)
suspicious_source_ip = Counter(record["source_ip"] for record in public_records).most_common(1)[0][0]
suspicious_records = [record for record in public_records if record["source_ip"] == suspicious_source_ip]


def first_matching(event_name: str) -> dict[str, str]:
    for record in suspicious_records:
        if record["event_name"] == event_name:
            return record
    raise RuntimeError(f"missing event {event_name}")


first_suspicious = suspicious_records[0]
list_access_keys = first_matching("ListAccessKeys")
create_access_key = first_matching("CreateAccessKey")
stop_logging = first_matching("StopLogging")

target_resource = None
for record in suspicious_records:
    if record["event_name"] == "GetObject" and record["resource"].startswith(SENSITIVE_BUCKET_PREFIX):
        target_resource = record
        break

if target_resource is None:
    raise RuntimeError("missing sensitive GetObject record")

report = {
    "compromised_user": compromised_user,
    "first_suspicious_event_time": first_suspicious["timestamp"],
    "suspicious_source_ip": suspicious_source_ip,
    "credential_event": create_access_key["event_name"],
    "target_resource": target_resource["resource"],
}
REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

timeline_rows = [
    first_suspicious,
    list_access_keys,
    create_access_key,
    target_resource,
    stop_logging,
]

with TIMELINE_PATH.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["timestamp", "event_name", "source_ip", "outcome", "resource"])
    for record in timeline_rows:
        writer.writerow(
            [
                record["timestamp"],
                record["event_name"],
                record["source_ip"],
                record["outcome"],
                record["resource"],
            ]
        )

with tarfile.open(BUNDLE_PATH, "w:gz") as tar:
    tar.add(REPORT_PATH, arcname="investigation_report.json")
    tar.add(TIMELINE_PATH, arcname="suspicious_activity.csv")
    for log_path in sorted(LOG_DIR.glob("*.json.gz")):
        tar.add(log_path, arcname=f"data/cloudtrail_logs/{log_path.name}")
PY
