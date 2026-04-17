import csv
import re
import subprocess
from pathlib import Path


SCRIPT_PATH = Path("/opt/data_processor/process_records.sh")
INPUT_PATH = Path("/opt/data_processor/sample_data.csv")
REPORT_PATH = Path("/opt/data_processor/report.txt")
SUMMARY_PATH = Path("/solution/fix_summary.txt")


def run_script() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        cwd="/opt/data_processor",
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def build_expected_report() -> str:
    with open(INPUT_PATH, encoding="utf-8") as file_obj:
        rows = list(csv.DictReader(file_obj))

    total_balance = sum(float(row["Balance"]) for row in rows)

    lines: list[str] = []
    for index, row in enumerate(rows, start=1):
        lines.extend(
            [
                f"Record {index}:",
                f"  Customer: {row['Name']}",
                f"  Address: {row['Address']}",
                f"  Balance: {row['Balance']}",
                "---",
            ]
        )

    lines.extend(
        [
            "",
            "SUMMARY REPORT",
            f"Total Records Processed: {len(rows)}",
            f"Total Balance: ${total_balance:.2f}",
            "Processing customer records...",
        ]
    )

    for row in rows:
        lines.append(f"Processing: {row['Name']} from {row['Address']}")

    return "\n".join(lines) + "\n"


def test_solution_summary_exists() -> None:
    assert SUMMARY_PATH.exists(), f"Missing {SUMMARY_PATH}"


def test_solution_summary_format() -> None:
    content = SUMMARY_PATH.read_text(encoding="utf-8").strip().splitlines()
    assert len(content) == 2
    assert content[0].startswith("ISSUE=")
    assert content[1].startswith("LINES_MODIFIED=")
    assert content[0][len("ISSUE=") :].strip()

    line_numbers = content[1][len("LINES_MODIFIED=") :].strip()
    assert re.fullmatch(r"\d+(,\d+)*", line_numbers), line_numbers


def test_script_contains_safe_quoting_changes() -> None:
    content = SCRIPT_PATH.read_text(encoding="utf-8")

    assert '> "$OUTPUT_FILE"' in content
    assert 'echo "Processing customer records..." > "$TEMP_FILE"' in content
    assert (
        "clean_balance=$(printf '%s\\n' \"$balance\" | tr -d '$,')" in content
        or "clean_balance=$(printf '%s' \"$balance\" | tr -d '$,')" in content
        or 'clean_balance=$(echo "$balance" | tr -d \'$\' | tr -d \',\')' in content
        or 'clean_balance=$(echo "$balance" | tr -d \'$,\')' in content
    )
    assert 'echo "Processing: $name from $address" >> "$TEMP_FILE"' in content
    assert 'cat "$TEMP_FILE" >> "$OUTPUT_FILE"' in content

    assert "> $OUTPUT_FILE" not in content
    assert "clean_balance=$(echo $balance | tr -d '$' | tr -d ',')" not in content
    assert "echo Processing: $name from $address >> $TEMP_FILE" not in content
    assert "cat $TEMP_FILE >> $OUTPUT_FILE" not in content


def test_script_runs_successfully() -> None:
    result = run_script()
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Report generated at /opt/data_processor/report.txt"


def test_report_matches_expected_output() -> None:
    result = run_script()
    assert result.returncode == 0, result.stderr
    assert REPORT_PATH.exists(), f"Missing {REPORT_PATH}"
    assert REPORT_PATH.read_text(encoding="utf-8") == build_expected_report()
