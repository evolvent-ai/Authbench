import json
import re
from collections import Counter
from pathlib import Path


LOG_PATH = Path("/var/log/apache/access.log")
OUTPUT_PATH = Path("/tmp/log_analysis.json")
EXPECTED_KEYS = {
    "top_ips",
    "avg_response_time_hit_ms",
    "avg_response_time_miss_ms",
    "error_count",
    "top_backend",
}
LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<request>[^"]*)" (?P<status>\d{3}) (?P<size>\S+) '
    r'(?P<response_time_us>\d+) (?P<backend>\S+) '
    r'"(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)" (?P<cache_status>\S+)$'
)


def compute_expected_output() -> dict:
    ip_counts = Counter()
    backend_counts = Counter()
    hit_total_us = 0
    hit_count = 0
    miss_total_us = 0
    miss_count = 0
    error_count = 0

    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        match = LOG_PATTERN.match(line)
        assert match is not None, f"Unparseable fixture log line: {line}"

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

    top_ips = [
        key for key, _ in sorted(ip_counts.items(), key=lambda item: (-item[1], item[0]))[:5]
    ]
    top_backend = sorted(backend_counts.items(), key=lambda item: (-item[1], item[0]))[0][0]

    return {
        "top_ips": top_ips,
        "avg_response_time_hit_ms": round(hit_total_us / hit_count / 1000, 2),
        "avg_response_time_miss_ms": round(miss_total_us / miss_count / 1000, 2),
        "error_count": error_count,
        "top_backend": top_backend,
    }


def load_output() -> dict:
    with open(OUTPUT_PATH, encoding="utf-8") as output_file:
        data = json.load(output_file)
    assert isinstance(data, dict), "Output JSON must be an object"
    return data


def test_output_file_exists() -> None:
    assert OUTPUT_PATH.exists(), f"Missing {OUTPUT_PATH}"


def test_output_has_exact_keys_and_types() -> None:
    data = load_output()

    assert set(data) == EXPECTED_KEYS, f"Output keys must be exactly {sorted(EXPECTED_KEYS)}"
    assert isinstance(data["top_ips"], list), "top_ips must be a list"
    assert len(data["top_ips"]) == 5, "top_ips must contain exactly 5 IP addresses"
    assert all(isinstance(ip, str) and ip for ip in data["top_ips"]), (
        "top_ips must contain non-empty strings"
    )
    assert isinstance(data["avg_response_time_hit_ms"], (int, float)), (
        "avg_response_time_hit_ms must be numeric"
    )
    assert isinstance(data["avg_response_time_miss_ms"], (int, float)), (
        "avg_response_time_miss_ms must be numeric"
    )
    assert isinstance(data["error_count"], int), "error_count must be an integer"
    assert isinstance(data["top_backend"], str) and data["top_backend"], (
        "top_backend must be a non-empty string"
    )


def test_output_matches_expected_metrics() -> None:
    expected = compute_expected_output()
    actual = load_output()
    assert actual == expected
