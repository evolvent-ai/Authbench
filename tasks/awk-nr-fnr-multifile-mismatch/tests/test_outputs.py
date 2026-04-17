import csv
import subprocess
from pathlib import Path


SCRIPT_PATH = Path("/solution/fixed_process_sales.awk")
EXPECTED_PATH = Path("/expected/correct_output.txt")
DATA_PATHS = [
    Path("/data/sales/region_north.csv"),
    Path("/data/sales/region_south.csv"),
    Path("/data/sales/region_west.csv"),
]


def build_expected_output() -> str:
    lines: list[str] = []
    overall_total = 0.0
    overall_records = 0

    for data_path in DATA_PATHS:
        rows = list(csv.DictReader(data_path.open(encoding="utf-8")))
        current_file = data_path.name
        region_name = current_file.removeprefix("region_").removesuffix(".csv")
        region_title = region_name.capitalize()
        region_total = sum(float(row["Amount"]) for row in rows)

        lines.append(f"Processing {current_file}...")
        for idx, row in enumerate(rows, start=2):
            lines.append(f"Processing line {idx} from file {current_file}")
            lines.append(
                "Date: "
                f"{row['Date']}, Product: {row['Product']}, "
                f"Amount: {float(row['Amount']):.2f}, Quantity: {row['Quantity']}"
            )

        lines.append("")
        lines.append(f"Region: {region_title} Summary")
        lines.append(f"Total Amount: {region_total:.2f}")
        lines.append(f"Total Records: {len(rows)}")
        lines.append("")

        overall_total += region_total
        overall_records += len(rows)

    lines.append("========================================")
    lines.append("OVERALL SUMMARY")
    lines.append("========================================")
    lines.append(f"Total Amount Across All Regions: {overall_total:.2f}")
    lines.append(f"Total Records Processed: {overall_records}")
    lines.append(f"Number of Regions: {len(DATA_PATHS)}")

    return "\n".join(lines) + "\n"


def run_fixed_script() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "awk",
            "-f",
            str(SCRIPT_PATH),
            *(str(data_path) for data_path in DATA_PATHS),
        ],
        capture_output=True,
        text=True,
    )


def test_fixed_script_exists() -> None:
    assert SCRIPT_PATH.exists(), f"Missing {SCRIPT_PATH}"
    assert SCRIPT_PATH.read_text(encoding="utf-8").strip(), "Script is empty"


def test_reference_output_matches_dataset() -> None:
    expected = build_expected_output()
    actual = EXPECTED_PATH.read_text(encoding="utf-8")
    assert actual == expected


def test_fixed_script_has_valid_awk_syntax() -> None:
    result = subprocess.run(
        ["awk", "--lint", "-f", str(SCRIPT_PATH), "/dev/null"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "fatal" not in result.stderr.lower(), result.stderr


def test_fixed_script_output_matches_expected() -> None:
    result = run_fixed_script()
    assert result.returncode == 0, result.stderr
    assert result.stdout == EXPECTED_PATH.read_text(encoding="utf-8")
