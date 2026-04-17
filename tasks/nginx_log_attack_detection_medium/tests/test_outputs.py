import json
import re
import tarfile
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, unquote_plus


INPUT_PATH = Path("/workdir/data/nginx/access.log")
OUTPUT_PATH = Path("/workdir/sql_injection_report.json")
BUNDLE_PATH = Path("/workdir/nginx_sqli_handoff.tar.gz")

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


def _load_output() -> dict[str, object]:
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def _decode_target(target: str) -> str:
    if "?" not in target:
        return unquote(target)
    path, query = target.split("?", 1)
    return unquote(path) + "?" + unquote_plus(query)


def _expected_report() -> dict[str, object]:
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
        assert match is not None, f"failed to parse log line: {line}"

        decoded_target = _decode_target(match.group("target"))
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

    return {
        "total_sqli_requests": total,
        "attack_ips": sorted(attack_ips),
        "attack_families_detected": sorted(families),
        "scanner_tools": sorted(tools),
        "status_breakdown": {code: status_counts[code] for code in sorted(status_counts)},
        "most_targeted_path": min(path for path, count in path_counts.items() if count == max(path_counts.values())),
        "highest_volume_ip": min(ip for ip, count in ip_counts.items() if count == max(ip_counts.values())),
    }


def test_output_exists() -> None:
    assert OUTPUT_PATH.exists(), "sql_injection_report.json was not created"


def test_output_matches_expected_report() -> None:
    assert _load_output() == _expected_report()


def test_expected_report_sanity() -> None:
    assert _expected_report() == {
        "total_sqli_requests": 49,
        "attack_ips": [
            "185.220.101.42",
            "198.51.100.23",
            "45.142.212.61",
            "91.203.5.146",
        ],
        "attack_families_detected": [
            "boolean_based",
            "error_based",
            "stacked_queries",
            "time_based",
            "union_based",
        ],
        "scanner_tools": [
            "curl",
            "python-requests",
            "scrapy",
        ],
        "status_breakdown": {
            "200": 8,
            "400": 3,
            "403": 21,
            "500": 17,
        },
        "most_targeted_path": "/products",
        "highest_volume_ip": "198.51.100.23",
    }


def test_bundle_exists() -> None:
    assert BUNDLE_PATH.exists(), "nginx_sqli_handoff.tar.gz was not created"


def test_bundle_contains_required_artifacts() -> None:
    with tarfile.open(BUNDLE_PATH, "r:gz") as tar:
        names = set(tar.getnames())

    expected_names = {
        "sql_injection_report.json",
        "data/nginx/access.log",
    }
    assert expected_names <= names
