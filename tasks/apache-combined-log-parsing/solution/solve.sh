#!/bin/bash
set -euo pipefail

python3 - <<'PY'
import json
import re
from collections import Counter
from pathlib import Path


LOG_PATH = Path("/var/log/apache/access.log")
OUTPUT_PATH = Path("/tmp/log_analysis.json")
LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<request>[^"]*)" (?P<status>\d{3}) (?P<size>\S+) '
    r'(?P<response_time_us>\d+) (?P<backend>\S+) '
    r'"(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)" (?P<cache_status>\S+)$'
)

ip_counts = Counter()
backend_counts = Counter()
hit_total_us = 0
hit_count = 0
miss_total_us = 0
miss_count = 0
error_count = 0

for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
    match = LOG_PATTERN.match(line)
    if not match:
        raise ValueError(f"Unparseable log line: {line}")

    ip = match.group("ip")
    status = int(match.group("status"))
    response_time_us = int(match.group("response_time_us"))
    backend = match.group("backend")
    cache_status = match.group("cache_status")

    ip_counts[ip] += 1
    backend_counts[backend] += 1

    if 400 <= status < 600:
        error_count += 1

    if cache_status == "HIT":
        hit_total_us += response_time_us
        hit_count += 1
    elif cache_status == "MISS":
        miss_total_us += response_time_us
        miss_count += 1


def rank_keys(counter: Counter[str], limit: int) -> list[str]:
    return [
        key for key, _ in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


result = {
    "top_ips": rank_keys(ip_counts, 5),
    "avg_response_time_hit_ms": round(hit_total_us / hit_count / 1000, 2) if hit_count else 0.0,
    "avg_response_time_miss_ms": round(miss_total_us / miss_count / 1000, 2)
    if miss_count
    else 0.0,
    "error_count": error_count,
    "top_backend": rank_keys(backend_counts, 1)[0],
}

OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
PY
