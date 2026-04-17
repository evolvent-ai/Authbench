#!/usr/bin/env python3

import argparse
import csv
import gzip
import json
from collections import Counter, defaultdict
from ipaddress import ip_address
from pathlib import Path


def _load_config(path: Path) -> dict[str, str]:
    config: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        config[key.strip()] = value.strip()
    return config


def _is_public_ip(value: str) -> bool:
    try:
        return not ip_address(value).is_private
    except ValueError:
        return False


def _extract_resource(record: dict) -> str:
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


def build_outputs(config_path: Path, logs_dir: Path, report_path: Path, csv_path: Path) -> None:
    config = _load_config(config_path)
    required_events = {
        part.strip() for part in config["required_events"].split(",") if part.strip()
    }
    sensitive_bucket_prefix = config["sensitive_bucket_prefix"]

    records: list[dict[str, str]] = []
    for log_path in sorted(logs_dir.glob("*.json.gz")):
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
                    "resource": _extract_resource(record),
                }
            )

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
        public_records = [record for record in user_records if _is_public_ip(record["source_ip"])]
        if not public_records:
            continue
        score = len(public_records) + sum(weights.get(record["event_name"], 0) for record in public_records)
        if score > best_score:
            best_score = score
            compromised_user = username

    if compromised_user is None:
        raise RuntimeError("could not identify compromised user")

    public_records = sorted(
        [record for record in records_by_user[compromised_user] if _is_public_ip(record["source_ip"])],
        key=lambda item: item["timestamp"],
    )
    suspicious_source_ip = Counter(record["source_ip"] for record in public_records).most_common(1)[0][0]
    suspicious_records = [
        record
        for record in public_records
        if record["source_ip"] == suspicious_source_ip and record["event_name"] in required_events
    ]

    filtered_rows: list[dict[str, str]] = []
    seen = set()
    for event_name in ["ListBuckets", "ListAccessKeys", "CreateAccessKey", "GetObject", "StopLogging"]:
        for record in suspicious_records:
            if record["event_name"] != event_name:
                continue
            if event_name == "GetObject" and not record["resource"].startswith(sensitive_bucket_prefix):
                continue
            marker = (record["timestamp"], record["event_name"])
            if marker in seen:
                continue
            seen.add(marker)
            filtered_rows.append(record)
            break

    if len(filtered_rows) != 5:
        raise RuntimeError("filtered suspicious sequence is incomplete")

    report = {
        "filter_name": config["filter_name"],
        "compromised_user": compromised_user,
        "suspicious_source_ip": suspicious_source_ip,
        "first_match_time": filtered_rows[0]["timestamp"],
        "matched_event_count": len(filtered_rows),
        "target_resource": filtered_rows[3]["resource"],
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "event_name", "source_ip", "outcome", "resource"])
        for record in filtered_rows:
            writer.writerow(
                [
                    record["timestamp"],
                    record["event_name"],
                    record["source_ip"],
                    record["outcome"],
                    record["resource"],
                ]
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--logs", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    args = parser.parse_args()
    build_outputs(args.config, args.logs, args.report, args.csv)


if __name__ == "__main__":
    main()
