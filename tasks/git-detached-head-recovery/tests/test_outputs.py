import json
import re
import subprocess
from pathlib import Path


REPO = "/workspace/project"
REPORT_PATH = Path("/workspace/recovery_report.json")
EXPECTED_SUBJECTS = [
    "Update error handling",
    "Add validation logic",
    "Fix bug in authentication",
]


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", REPO, *args],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def load_report() -> dict:
    assert REPORT_PATH.exists(), "recovery_report.json file does not exist at /workspace/"
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def test_recovered_branch_exists():
    assert git("branch", "--list", "recovered-work"), "Branch 'recovered-work' does not exist"


def test_recovery_report_structure():
    data = load_report()
    assert set(data) == {"recovered_branch", "commit_count", "latest_commit_hash"}
    assert data["recovered_branch"] == "recovered-work"
    assert data["commit_count"] == 3
    assert re.fullmatch(r"[0-9a-f]{40}", data["latest_commit_hash"])


def test_recovery_report_matches_branch_tip():
    data = load_report()
    assert git("rev-parse", "recovered-work") == data["latest_commit_hash"]


def test_recovered_commits_match_detached_session():
    subjects = git("log", "--format=%s", "recovered-work", "^main").splitlines()
    assert subjects == EXPECTED_SUBJECTS

    commits = [line for line in git("rev-list", "recovered-work", "^main").splitlines() if line]
    assert len(commits) == 3


def test_main_branch_was_not_modified():
    expected_main = Path("/workspace/original_main_sha.txt").read_text(encoding="utf-8").strip()
    assert git("rev-parse", "main") == expected_main
