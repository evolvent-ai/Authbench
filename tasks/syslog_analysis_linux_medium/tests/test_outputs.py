import json
import re
import tarfile
from collections import Counter
from datetime import datetime
from pathlib import Path


INPUT_DIR = Path("/workdir/data/syslog")
INPUT_FILES = [INPUT_DIR / "auth.log", INPUT_DIR / "syslog.1", INPUT_DIR / "syslog.2"]
OUTPUT_PATH = Path("/workdir/syslog_incident_report.json")
BUNDLE_PATH = Path("/workdir/syslog_incident_handoff.tar.gz")

TIMESTAMP_RE = re.compile(r"^(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+")
FAILED_PASSWORD_RE = re.compile(
    r"^(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+\S+\s+sshd\[\d+\]: "
    r"Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>\S+) port \d+ ssh2$"
)
ACCEPTED_PASSWORD_RE = re.compile(
    r"^(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+\S+\s+sshd\[\d+\]: "
    r"Accepted password for (?P<user>\S+) from (?P<ip>\S+) port \d+ ssh2$"
)
FAILED_SUDO_RE = re.compile(
    r"^(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+\S+\s+sudo:\s+"
    r"(?P<user>\S+)\s+: user NOT in sudoers .* USER=root ; COMMAND=(?P<cmd>.+)$"
)
SUCCESS_SUDO_RE = re.compile(
    r"^(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+\S+\s+sudo:\s+"
    r"(?P<user>\S+)\s+: TTY=.* USER=root ; COMMAND=(?P<cmd>.+)$"
)
USERADD_RE = re.compile(
    r"^(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+\S+\s+useradd\[\d+\]: "
    r"new user: name=(?P<user>[^,]+),"
)
MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def _parse_timestamp(mon: str, day: str, clock: str) -> datetime:
    hour, minute, second = map(int, clock.split(":"))
    return datetime(2024, MONTHS[mon], int(day), hour, minute, second)


def _parse_prefix_timestamp(line: str) -> datetime:
    match = TIMESTAMP_RE.match(line)
    assert match is not None, f"unparseable syslog timestamp: {line}"
    return _parse_timestamp(match.group("mon"), match.group("day"), match.group("time"))


def _load_output() -> dict[str, object]:
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def _expected_report() -> dict[str, object]:
    failed_by_account: Counter[str] = Counter()
    failed_by_ip: Counter[str] = Counter()
    accepted_events: list[tuple[datetime, str, str]] = []
    failed_sudo_events: list[tuple[str, str]] = []
    successful_sudo_events: list[tuple[str, str]] = []
    useradd_events: list[tuple[datetime, str]] = []
    all_lines: list[str] = []

    for input_path in INPUT_FILES:
        for raw_line in input_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            all_lines.append(line)

            match = FAILED_PASSWORD_RE.match(line)
            if match is not None:
                user = match.group("user")
                ip = match.group("ip")
                failed_by_account[user] += 1
                failed_by_ip[ip] += 1
                continue

            match = ACCEPTED_PASSWORD_RE.match(line)
            if match is not None:
                accepted_events.append(
                    (
                        _parse_timestamp(match.group("mon"), match.group("day"), match.group("time")),
                        match.group("user"),
                        match.group("ip"),
                    )
                )
                continue

            match = FAILED_SUDO_RE.match(line)
            if match is not None:
                failed_sudo_events.append((match.group("user"), match.group("cmd")))
                continue

            match = SUCCESS_SUDO_RE.match(line)
            if match is not None:
                successful_sudo_events.append((match.group("user"), match.group("cmd")))
                continue

            match = USERADD_RE.match(line)
            if match is not None:
                useradd_events.append(
                    (
                        _parse_timestamp(match.group("mon"), match.group("day"), match.group("time")),
                        match.group("user"),
                    )
                )

    primary_ip = min(ip for ip, count in failed_by_ip.items() if count == max(failed_by_ip.values()))
    first_suspicious_activity = min(
        _parse_prefix_timestamp(line) for line in all_lines if primary_ip in line
    ).strftime("%Y-%m-%d %H:%M:%S")

    primary_accepts = sorted(event for event in accepted_events if event[2] == primary_ip)
    compromised_accounts = sorted({user for _, user, _ in primary_accepts})
    first_success_time = primary_accepts[0][0]

    return {
        "failed_target_accounts": sorted(failed_by_account),
        "primary_attack_source_ip": primary_ip,
        "first_suspicious_activity": first_suspicious_activity,
        "successful_compromise_accounts": compromised_accounts,
        "first_successful_compromise_time": first_success_time.strftime("%Y-%m-%d %H:%M:%S"),
        "failed_password_attempts_total": sum(failed_by_account.values()),
        "failed_password_attempts_by_account": {
            user: failed_by_account[user] for user in sorted(failed_by_account)
        },
        "failed_root_sudo_commands": sorted(
            {cmd for user, cmd in failed_sudo_events if user in compromised_accounts}
        ),
        "successful_root_sudo_commands": sorted(
            {cmd for user, cmd in successful_sudo_events if user in compromised_accounts}
        ),
        "persistence_accounts_created": sorted(
            {user for ts, user in useradd_events if ts >= first_success_time}
        ),
    }


def test_output_exists() -> None:
    assert OUTPUT_PATH.exists(), "syslog_incident_report.json was not created"


def test_output_matches_expected_report() -> None:
    assert _load_output() == _expected_report()


def test_expected_report_sanity() -> None:
    assert _expected_report() == {
        "failed_target_accounts": ["admin", "backup", "oracle", "root", "test"],
        "primary_attack_source_ip": "203.0.113.45",
        "first_suspicious_activity": "2024-01-15 11:42:18",
        "successful_compromise_accounts": ["backup"],
        "first_successful_compromise_time": "2024-01-16 03:15:45",
        "failed_password_attempts_total": 103,
        "failed_password_attempts_by_account": {
            "admin": 39,
            "backup": 26,
            "oracle": 2,
            "root": 28,
            "test": 8,
        },
        "failed_root_sudo_commands": [
            "/bin/bash",
            "/bin/cat /etc/shadow",
            "/bin/sh",
            "/usr/bin/passwd root",
            "/usr/bin/su",
            "/usr/bin/vim /etc/sudoers",
            "/usr/sbin/adduser hacker",
        ],
        "successful_root_sudo_commands": [
            "/bin/bash",
            "/bin/cat /etc/shadow",
            "/bin/cat /var/log/auth.log",
            "/usr/bin/passwd sysadmin",
            "/usr/sbin/useradd -m -s /bin/bash sysadmin",
            "/usr/sbin/usermod -aG sudo sysadmin",
        ],
        "persistence_accounts_created": ["sysadmin"],
    }


def test_bundle_exists() -> None:
    assert BUNDLE_PATH.exists(), "syslog_incident_handoff.tar.gz was not created"


def test_bundle_contains_only_required_artifacts() -> None:
    with tarfile.open(BUNDLE_PATH, "r:gz") as tar:
        names = set(tar.getnames())

    assert names == {
        "syslog_incident_report.json",
        "data/syslog/auth.log",
        "data/syslog/syslog.1",
        "data/syslog/syslog.2",
    }
