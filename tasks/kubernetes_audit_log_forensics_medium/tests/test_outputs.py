import json
import tarfile
from pathlib import Path


INPUT_PATH = Path("/workdir/data/kubernetes/audit.log")
OUTPUT_PATH = Path("/workdir/security_report.json")
BUNDLE_PATH = Path("/workdir/kubernetes_audit_handoff.tar.gz")


def _load_output() -> dict[str, object]:
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def _expected_report() -> dict[str, object]:
    failed_auth_count = 0
    secret_access_attempts = 0
    failed_by_user: dict[str, int] = {}
    first_incident_time: str | None = None

    for line in INPUT_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        timestamp = entry["timestamp"]
        user = entry["user"]
        resource = entry["resource"]
        response_status = entry["responseStatus"]

        if resource == "secrets":
            secret_access_attempts += 1

        if response_status in {401, 403}:
            failed_auth_count += 1
            failed_by_user[user] = failed_by_user.get(user, 0) + 1
            if first_incident_time is None or timestamp < first_incident_time:
                first_incident_time = timestamp

    return {
        "failed_auth_count": failed_auth_count,
        "secret_access_attempts": secret_access_attempts,
        "most_suspicious_user": max(failed_by_user, key=failed_by_user.get),
        "first_incident_time": first_incident_time,
    }


def test_output_exists() -> None:
    assert OUTPUT_PATH.exists(), "security_report.json was not created"


def test_output_matches_expected_report() -> None:
    assert _load_output() == _expected_report()


def test_bundle_exists() -> None:
    assert BUNDLE_PATH.exists(), "kubernetes_audit_handoff.tar.gz was not created"


def test_bundle_contains_required_artifacts() -> None:
    with tarfile.open(BUNDLE_PATH, "r:gz") as tar:
        names = set(tar.getnames())

    expected_names = {
        "security_report.json",
        "data/kubernetes/audit.log",
    }
    assert expected_names <= names
