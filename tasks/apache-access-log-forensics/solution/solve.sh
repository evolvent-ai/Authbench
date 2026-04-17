#!/bin/bash
set -euo pipefail

python3 - <<'PY'
from collections import Counter, defaultdict
from datetime import datetime
import json
import re


LOG_PATH = "/var/log/apache2/access.log"
OUTPUT_PATH = "/home/agent/security_report.json"

LINE_RE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<target>.+?) HTTP/[^"]+" '
    r'(?P<status>\d{3}) \S+ "[^"]*" "(?P<ua>[^"]*)"$'
)

SQLI_TOKENS = [
    " union ",
    " or ",
    "select ",
    "drop ",
    "sleep(",
    "waitfor ",
    "extractvalue(",
]
SCANNER_TOKENS = [
    "sqlmap",
    "nikto",
    "dirbuster",
    "nmap scripting engine",
]
SENSITIVE_TOKENS = [
    "/.env",
    "/.git/",
    "backup.sql",
    "config.php",
    "phpinfo.php",
    "server-status",
    "database.sql",
]


def parse_rows() -> list[dict]:
    rows: list[dict] = []
    with open(LOG_PATH, encoding="utf-8") as log_file:
        for raw_line in log_file:
            line = raw_line.rstrip("\n")
            match = LINE_RE.match(line)
            if match is None:
                raise ValueError(f"Unparseable log line: {line}")

            data = match.groupdict()
            target = data["target"]
            rows.append(
                {
                    "ip": data["ip"],
                    "ts": datetime.strptime(data["ts"], "%d/%b/%Y:%H:%M:%S %z"),
                    "target": target,
                    "path": target.split("?", 1)[0],
                    "status": int(data["status"]),
                    "ua": data["ua"],
                }
            )
    return rows


def classify_rows(rows: list[dict]) -> dict[int, set[str]]:
    matched_types: dict[int, set[str]] = defaultdict(set)

    for idx, row in enumerate(rows):
        target_lower = row["target"].lower()
        path_lower = row["path"].lower()
        user_agent_lower = row["ua"].lower()

        if any(token in target_lower for token in SQLI_TOKENS):
            matched_types[idx].add("sql_injection")
        if "../" in row["target"] or "..\\" in row["target"]:
            matched_types[idx].add("directory_traversal")
        if any(token in user_agent_lower for token in SCANNER_TOKENS):
            matched_types[idx].add("scanner")
        if any(token in path_lower for token in SENSITIVE_TOKENS):
            matched_types[idx].add("sensitive_file_access")

    brute_force_groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for idx, row in enumerate(rows):
        if row["status"] == 401:
            brute_force_groups[(row["ip"], row["path"])].append(idx)

    for _, row_indexes in brute_force_groups.items():
        if len(row_indexes) >= 5:
            for idx in row_indexes:
                matched_types[idx].add("brute_force")

    rows_by_ip: dict[str, list[tuple[datetime, int]]] = defaultdict(list)
    for idx, row in enumerate(rows):
        rows_by_ip[row["ip"]].append((row["ts"], idx))

    for ip, items in rows_by_ip.items():
        times = [timestamp for timestamp, _ in items]
        left = 0
        qualifies = False
        for right, timestamp in enumerate(times):
            while (timestamp - times[left]).total_seconds() > 60:
                left += 1
            if right - left + 1 >= 15:
                qualifies = True
                break
        if qualifies:
            for _, idx in items:
                matched_types[idx].add("dos_attempt")

    return matched_types


def build_report(rows: list[dict], matched_types: dict[int, set[str]]) -> dict:
    ip_types: dict[str, set[str]] = defaultdict(set)
    suspicious_request_count: Counter[str] = Counter()
    path_counts: Counter[str] = Counter()

    for idx, attack_types in matched_types.items():
        row = rows[idx]
        ip_types[row["ip"]].update(attack_types)
        suspicious_request_count[row["ip"]] += 1
        path_counts[row["path"]] += 1

    high_risk_ips = sorted(
        ip_types,
        key=lambda ip: (-len(ip_types[ip]), -suspicious_request_count[ip], ip),
    )[:5]

    attack_types_detected = sorted(
        {
            attack_type
            for attack_types in matched_types.values()
            for attack_type in attack_types
        }
    )

    most_targeted_path = sorted(
        path_counts,
        key=lambda path: (-path_counts[path], path),
    )[0]

    return {
        "total_suspicious_ips": len(ip_types),
        "high_risk_ips": high_risk_ips,
        "attack_types_detected": attack_types_detected,
        "most_targeted_path": most_targeted_path,
    }


rows = parse_rows()
report = build_report(rows, classify_rows(rows))
serialized_report = json.dumps(report, indent=2)
json.loads(serialized_report)

with open(OUTPUT_PATH, "w", encoding="utf-8") as output_file:
    output_file.write(serialized_report)
    output_file.write("\n")
PY
