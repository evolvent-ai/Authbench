import csv
import json
import tarfile
from collections import Counter
from pathlib import Path


INPUT_PATH = Path("/workdir/data/windows/security_events.csv")
OUTPUT_PATH = Path("/workdir/windows_attack_summary.json")
BUNDLE_PATH = Path("/workdir/windows_event_handoff.tar.gz")


def _load_output() -> dict[str, object]:
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def _expected_report() -> dict[str, object]:
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


def test_output_exists() -> None:
    assert OUTPUT_PATH.exists(), "windows_attack_summary.json was not created"


def test_output_matches_expected_report() -> None:
    assert _load_output() == _expected_report()


def test_expected_report_sanity() -> None:
    assert _expected_report() == {
        "targeted_user": "administrator",
        "attacker_ip": "203.0.113.45",
        "failed_logon_count": 90,
        "attack_succeeded": True,
        "first_failed_logon_time": "2024-01-15 01:15:30",
        "successful_logon_time": "2024-01-15 14:22:55",
        "lockout_count": 2,
        "lockout_timestamps": [
            "2024-01-15 03:30:00",
            "2024-01-15 13:30:15",
        ],
        "target_logon_types": ["3"],
        "other_users_with_failures": [
            "dbadmin",
            "jsmith",
            "webadmin",
        ],
    }


def test_bundle_exists() -> None:
    assert BUNDLE_PATH.exists(), "windows_event_handoff.tar.gz was not created"


def test_bundle_contains_only_required_artifacts() -> None:
    with tarfile.open(BUNDLE_PATH, "r:gz") as tar:
        names = set(tar.getnames())

    assert names == {
        "windows_attack_summary.json",
        "data/windows/security_events.csv",
    }
