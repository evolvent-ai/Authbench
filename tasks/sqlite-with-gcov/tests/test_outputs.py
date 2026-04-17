import os
import shutil
import subprocess


def test_sqlite_compiled():
    result = subprocess.run(
        ["sqlite3", ":memory:", "SELECT sqlite_version();"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"SQLite execution failed: {result.stderr}"
    assert result.stdout.strip(), "SQLite version output is empty"


def test_sqlite_in_path():
    sqlite_path = shutil.which("sqlite3")
    assert sqlite_path is not None, "sqlite3 not found in PATH"

    result = subprocess.run(
        ["sqlite3", ":memory:", "SELECT 1;"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"SQLite execution from PATH failed: {result.stderr}"


def test_gcov_enabled():
    result = subprocess.run(
        ["sqlite3", ":memory:", "SELECT 1;"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "Failed to run SQLite"

    gcda_files = []
    gcno_files = []
    for root, _, files in os.walk("/app/sqlite"):
        for name in files:
            path = os.path.join(root, name)
            if name.endswith(".gcda"):
                gcda_files.append(path)
            if name.endswith(".gcno"):
                gcno_files.append(path)

    assert gcda_files, "No .gcda files found, gcov instrumentation may not be enabled"
    assert gcno_files, "No .gcno files found, gcov instrumentation may not be enabled"
