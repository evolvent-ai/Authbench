#!/usr/bin/env bash
set -euo pipefail

/usr/bin/python3 - <<'PY'
import json
import re
import tarfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote

NOTE_PATH = Path("/workdir/apache_handoff_note.txt")
INPUT_PATH = Path("/workdir/data/apache/access.log")
OUTPUT_PATH = Path("/workdir/security_report.json")
BUNDLE_PATH = Path("/workdir/apache_access_handoff.tar.gz")

NOTE_PATH.read_text(encoding="utf-8")

LINE_RE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] "(?P<method>\S+) (?P<target>.+) '
    r'(?P<proto>HTTP/[^\s]+)" (?P<status>\d{3}) (?P<size>\S+) "(?P<ref>[^"]*)" '
    r'"(?P<ua>[^"]*)"$'
)
SQLI_PATTERNS = (
    "' or '",
    "union select",
    "union all select",
    "drop table",
    "select * from",
    "and 1=1",
    "'--",
    "--",
    "; select",
    "; drop",
)
SCANNER_AGENTS = ("sqlmap", "nikto", "nmap", "masscan", "python-urllib", "python-requests")
SENSITIVE_PATHS = {"/.env", "/.git/config", "/config.php", "/backup.sql", "/phpinfo.php"}

requests_by_ip: dict[str, list[tuple[str, int]]] = defaultdict(list)
categories_by_ip: dict[str, set[str]] = defaultdict(set)
path_counter: Counter[str] = Counter()

for raw_line in INPUT_PATH.read_text(encoding="utf-8").splitlines():
    line = raw_line.strip()
    if not line:
        continue
    match = LINE_RE.match(line)
    if match is None:
        raise ValueError(f"unparseable access-log line: {line}")

    ip = match.group("ip")
    decoded_target = unquote(match.group("target"))
    path = decoded_target.split("?", 1)[0]
    status = int(match.group("status"))
    ua = match.group("ua").lower()
    lower_target = decoded_target.lower()
    lower_path = path.lower()

    requests_by_ip[ip].append((path, status))
    path_counter[path] += 1

    if "?" in decoded_target and any(token in lower_target for token in SQLI_PATTERNS):
        categories_by_ip[ip].add("sql_injection")
    if any(token in lower_path for token in ("../", "..\\")) or "/.." in lower_path:
        categories_by_ip[ip].add("directory_traversal")
    if any(agent in ua for agent in SCANNER_AGENTS):
        categories_by_ip[ip].add("scanner")
    if lower_path in SENSITIVE_PATHS:
        categories_by_ip[ip].add("sensitive_file_access")

for ip, requests in requests_by_ip.items():
    brute_force_hits = sum(1 for path, status in requests if path == "/admin/login.php" and status == 401)
    if brute_force_hits >= 6:
        categories_by_ip[ip].add("brute_force")
    if len(requests) >= 20:
        categories_by_ip[ip].add("dos_attempt")

report = {
    "total_suspicious_ips": len(categories_by_ip),
    "high_risk_ips": sorted(ip for ip, categories in categories_by_ip.items() if len(categories) >= 2),
    "attack_types_detected": sorted({category for categories in categories_by_ip.values() for category in categories}),
    "most_targeted_path": path_counter.most_common(1)[0][0],
}
OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

with tarfile.open(BUNDLE_PATH, "w:gz") as tar:
    tar.add(OUTPUT_PATH, arcname="security_report.json")
    tar.add(INPUT_PATH, arcname="data/apache/access.log")
PY
