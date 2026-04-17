import subprocess
from pathlib import Path

REPO_ROOT = Path("/app/dclm")
EXPECTED_ROOT = Path("/tests/expected")
SECRET_LITERALS = [
    "AKIA1234567890123456",
    "D4w8z9wKN1aVeT3BpQj6kIuN7wH8X0M9KfV5OqzF",
    "ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789",
    "hf_abcdefghijklmnopqrstuvwxyz123456",
]
EXPECTED_TRACKED_FILES = {
    "ray_processing/process.py": EXPECTED_ROOT / "process.py",
    "ray_processing/ray_cluster.yaml": EXPECTED_ROOT / "ray_cluster.yaml",
}


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_repo_is_a_git_repository():
    assert _git("rev-parse", "--is-inside-work-tree") == "true"


def test_only_expected_tracked_files_exist():
    tracked_files = {
        line for line in _git("ls-files").splitlines() if line
    }
    assert tracked_files == set(EXPECTED_TRACKED_FILES)


def test_secrets_removed_from_tracked_files():
    tracked_files = {
        line for line in _git("ls-files").splitlines() if line
    }
    for relative_path in tracked_files:
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        lowered = content.lower()
        for secret in SECRET_LITERALS:
            assert secret.lower() not in lowered, (
                f"Secret literal still present in {relative_path}"
            )


def test_sanitized_snapshot_matches_expected():
    for relative_path, expected_path in EXPECTED_TRACKED_FILES.items():
        actual_text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        expected_text = expected_path.read_text(encoding="utf-8")
        assert actual_text == expected_text, f"Unexpected contents for {relative_path}"
