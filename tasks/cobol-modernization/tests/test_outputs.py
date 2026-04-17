from pathlib import Path
import subprocess


INITIAL_ACCOUNTS = (
    "U001John Doe            0000001000"
    "U002Jane Smith          0000002000"
    "U003Bob Wilson          0000001500"
)
INITIAL_BOOKS = (
    "B001Python Basics       U001"
    "B002COBOL Guide         U002"
    "B003Java Tutorial       U003"
)


def reset_fixtures() -> None:
    data_dir = Path("/app/data")
    (data_dir / "ACCOUNTS.DAT").write_text(INITIAL_ACCOUNTS, encoding="utf-8")
    (data_dir / "BOOKS.DAT").write_text(INITIAL_BOOKS, encoding="utf-8")
    (data_dir / "TRANSACTIONS.DAT").write_text("", encoding="utf-8")


def run_program(input_record: str) -> subprocess.CompletedProcess[str]:
    Path("/app/src/INPUT.DAT").write_text(input_record, encoding="utf-8")
    return subprocess.run(
        ["/usr/local/bin/python3", "/app/program.py"],
        capture_output=True,
        text=True,
        check=False,
    )


def test_required_files_exist():
    assert Path("/app/program.py").exists()
    assert Path("/app/src/program.cbl").exists()


def test_program_matches_expected_mutations():
    reset_fixtures()

    for input_record in (
        "U001U003B0030000000020",
        "U002U001B0030000000050",
        "U002U001B0010000000150",
    ):
        result = run_program(input_record)
        assert result.returncode == 0, result.stderr

    data_dir = Path("/app/data")
    assert (data_dir / "ACCOUNTS.DAT").read_text(encoding="utf-8") == (
        "U001John Doe            0000001180"
        "U002Jane Smith          0000001800"
        "U003Bob Wilson          0000001520"
    )
    assert (data_dir / "BOOKS.DAT").read_text(encoding="utf-8") == (
        "B001Python Basics       U002"
        "B002COBOL Guide         U002"
        "B003Java Tutorial       U002"
    )
    assert (data_dir / "TRANSACTIONS.DAT").read_text(encoding="utf-8") == (
        "B0030000000020U003U001"
        "B0030000000050U001U002"
        "B0010000000150U001U002"
    )
