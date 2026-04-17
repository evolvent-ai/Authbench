import re
import subprocess
from collections import Counter
from pathlib import Path


ORIGINAL_SCRIPT = Path("/opt/monitor/process_logs.sh")
FIXED_SCRIPT = Path("/opt/monitor/process_logs_fixed.sh")
VALID_LOG = Path("/workspace/data/server_valid.log")
CORRUPTED_LOG = Path("/workspace/data/server_corrupted.log")


def run_script(log_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(FIXED_SCRIPT), str(log_path)],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def parse_valid_error_lines(log_path: Path) -> list[list[str]]:
    parsed: list[list[str]] = []
    for raw_line in log_path.read_text(encoding="utf-8").splitlines():
        fields = raw_line.split()
        if len(fields) >= 5 and fields[2] == "ERROR":
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields[0]), raw_line
            assert re.fullmatch(r"\d{2}:\d{2}:\d{2}", fields[1]), raw_line
            assert re.fullmatch(r"\d+", fields[3]), raw_line
            parsed.append(fields)
    return parsed


def build_expected_stdout(log_path: Path) -> str:
    error_lines = parse_valid_error_lines(log_path)
    counts = Counter(fields[4] for fields in error_lines if int(fields[3]) >= 3)

    lines = [
        "=== Server Log Monitor ===",
        f"Processing logs from: {log_path}",
        "",
        "Stage 1: Extracting error entries...",
        "Stage 2: Filtering by severity level (>= 3)...",
        "Stage 3: Aggregating statistics...",
        "Stage 4: Formatting report...",
        "",
    ]

    for error_type in sorted(counts):
        lines.append(f"{error_type}: {counts[error_type]} occurrences")

    lines.extend(
        [
            "",
            "=== Report Complete ===",
            "Log processing finished successfully",
            "",
            "=== Summary Statistics ===",
            f"Total errors found: {len(error_lines)}",
            "",
            "Critical errors (severity >= 3):",
            f"Count: {sum(1 for fields in error_lines if int(fields[3]) >= 3)}",
            "",
            "Monitoring complete",
        ]
    )

    return "\n".join(lines) + "\n"


def expected_report_lines(log_path: Path) -> list[str]:
    error_lines = parse_valid_error_lines(log_path)
    counts = Counter(fields[4] for fields in error_lines if int(fields[3]) >= 3)
    return [f"{error_type}: {counts[error_type]} occurrences" for error_type in sorted(counts)]


def test_fixed_script_exists() -> None:
    assert FIXED_SCRIPT.exists(), f"Missing {FIXED_SCRIPT}"


def test_fixed_script_is_executable() -> None:
    assert FIXED_SCRIPT.stat().st_mode & 0o111, "Fixed script is not executable"


def test_original_script_is_present() -> None:
    assert ORIGINAL_SCRIPT.exists(), f"Missing {ORIGINAL_SCRIPT}"


def test_fixed_script_uses_pipefail_or_pipestatus() -> None:
    content = FIXED_SCRIPT.read_text(encoding="utf-8")
    has_pipefail = "set -o pipefail" in content or "set -euo pipefail" in content or "set -eo pipefail" in content
    has_pipestatus = "PIPESTATUS" in content or "${PIPESTATUS" in content
    assert has_pipefail or has_pipestatus


def test_valid_log_output_matches_expected() -> None:
    result = run_script(VALID_LOG)
    assert result.returncode == 0, result.stderr
    stdout = result.stdout
    assert "=== Server Log Monitor ===" in stdout
    assert "Stage 1: Extracting error entries..." in stdout
    assert "Stage 2: Filtering by severity level (>= 3)..." in stdout
    assert "Stage 3: Aggregating statistics..." in stdout
    assert "Stage 4: Formatting report..." in stdout
    assert "=== Report Complete ===" in stdout
    assert "=== Summary Statistics ===" in stdout
    assert f"Total errors found: {len(parse_valid_error_lines(VALID_LOG))}" in stdout
    assert f"Count: {sum(1 for fields in parse_valid_error_lines(VALID_LOG) if int(fields[3]) >= 3)}" in stdout
    assert "Monitoring complete" in stdout
    for line in expected_report_lines(VALID_LOG):
        assert line in stdout


def test_corrupted_log_fails() -> None:
    result = run_script(CORRUPTED_LOG)
    assert result.returncode != 0, "Corrupted log should cause a non-zero exit"
