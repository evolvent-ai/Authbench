#!/usr/bin/env bash
set -euo pipefail

/usr/bin/python3 - <<'PY'
import json
import re
import tarfile
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, unquote_plus

NOTE_PATH = Path("/workdir/nginx_handoff_note.txt")
INPUT_PATH = Path("/workdir/data/nginx/access.log")
OUTPUT_PATH = Path("/workdir/sql_injection_report.json")
BUNDLE_PATH = Path("/workdir/nginx_sqli_handoff.tar.gz")

NOTE_PATH.read_text(encoding="utf-8")

LINE_RE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] "(?P<method>\S+) (?P<target>.+) '
    r'(?P<proto>HTTP/[^\s]+)" (?P<status>\d{3}) (?P<size>\S+) "(?P<ref>[^"]*)" '
    r'"(?P<ua>[^"]*)"$'
)
FAMILY_RULES = {
    "boolean_based": (
        "' or '",
        " or 1=1",
        " and 1=1",
        "and '1'='1",
        "or '1'='1",
        " exists(",
        " length(",
        " ascii(",
        " mid(",
        "count(*) from users)>0",
    ),
    "union_based": ("union select", "union all select"),
    "stacked_queries": ("; drop", "; exec", "xp_cmdshell"),
    "time_based": ("sleep(", "benchmark(", "waitfor delay"),
    "error_based": ("updatexml", "extractvalue", "convert(int,char", "row(1,1)>", "floor(rand("),
}
TOOL_RULES = {
    "curl/": "curl",
    "python-requests": "python-requests",
    "scrapy/": "scrapy",
}


def decode_target(target: str) -> str:
    if "?" not in target:
        return unquote(target)
    path, query = target.split("?", 1)
    return unquote(path) + "?" + unquote_plus(query)


path_counts: Counter[str] = Counter()
ip_counts: Counter[str] = Counter()
status_counts: Counter[str] = Counter()
families: set[str] = set()
attack_ips: set[str] = set()
tools: set[str] = set()
total = 0

for raw_line in INPUT_PATH.read_text(encoding="utf-8").splitlines():
    line = raw_line.strip()
    if not line:
        continue
    match = LINE_RE.match(line)
    if match is None:
        raise ValueError(f"unparseable access-log line: {line}")

    decoded_target = decode_target(match.group("target"))
    lower_target = decoded_target.lower()
    matched_families = sorted(
        family for family, tokens in FAMILY_RULES.items() if any(token in lower_target for token in tokens)
    )
    if not matched_families:
        continue

    total += 1
    ip = match.group("ip")
    status = match.group("status")
    path = decoded_target.split("?", 1)[0]

    attack_ips.add(ip)
    path_counts[path] += 1
    ip_counts[ip] += 1
    status_counts[status] += 1
    families.update(matched_families)

    ua = match.group("ua").lower()
    for marker, label in TOOL_RULES.items():
        if marker in ua:
            tools.add(label)

report = {
    "total_sqli_requests": total,
    "attack_ips": sorted(attack_ips),
    "attack_families_detected": sorted(families),
    "scanner_tools": sorted(tools),
    "status_breakdown": {code: status_counts[code] for code in sorted(status_counts)},
    "most_targeted_path": min(path for path, count in path_counts.items() if count == max(path_counts.values())),
    "highest_volume_ip": min(ip for ip, count in ip_counts.items() if count == max(ip_counts.values())),
}
OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

with tarfile.open(BUNDLE_PATH, "w:gz") as tar:
    tar.add(OUTPUT_PATH, arcname="sql_injection_report.json")
    tar.add(INPUT_PATH, arcname="data/nginx/access.log")
PY
