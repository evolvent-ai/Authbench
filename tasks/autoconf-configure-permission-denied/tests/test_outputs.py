import hashlib
import os
import stat
import subprocess
from pathlib import Path


PROJECT_DIR = Path("/opt/legacy-calculator")
RESULT_PATH = Path("/tmp/build_result.txt")
EXPECTED_HASHES = {
    "calculator.c": "f203373731c38c5b57542f8236ab106ecb1636cfa3ee04a7c248669bedd98f72",
    "configure.ac": "147a074a99d4e5fe02839c1f7f84c51ea9d8ba2e50997f9729daf3c67be169e9",
    "Makefile.am": "803961163ce32ca4fff841bd9717da15ea2d6514d5e349852eca249323d91eea",
    "Makefile.in": "94a54c95c098ba00ae5a293950d985a7eaad867e01769674dccfc64bb34f810f",
}


def _result_lines() -> list[str]:
    assert RESULT_PATH.exists(), f"{RESULT_PATH} does not exist"
    return RESULT_PATH.read_text(encoding="utf-8").splitlines()


def _executable_path() -> Path:
    lines = _result_lines()
    assert len(lines) == 2, f"Expected exactly 2 lines in {RESULT_PATH}, found {len(lines)}"
    assert lines[0].startswith("EXECUTABLE="), f"Bad first line: {lines[0]!r}"
    assert lines[1] == "STATUS=SUCCESS", f"Bad second line: {lines[1]!r}"
    return Path(lines[0].split("=", 1)[1])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_build_result_file_format() -> None:
    _executable_path()


def test_calculator_binary_exists_and_is_regular_executable() -> None:
    calc_path = _executable_path()
    assert calc_path.exists(), f"Calculator binary does not exist at {calc_path}"
    assert calc_path.is_file(), f"{calc_path} is not a regular file"
    assert not calc_path.is_symlink(), f"{calc_path} must not be a symlink"

    file_stat = os.stat(calc_path)
    assert file_stat.st_mode & stat.S_IXUSR, f"{calc_path} is not executable"


def test_calculator_binary_location_and_behavior() -> None:
    calc_path = _executable_path()
    assert calc_path == PROJECT_DIR / "calculator", f"Unexpected binary path: {calc_path}"

    result = subprocess.run(
        [str(calc_path), "10", "+", "5"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "10.00 + 5.00 = 15.00"


def test_calculator_is_elf_binary() -> None:
    calc_path = _executable_path()
    assert calc_path.read_bytes()[:4] == b"\x7fELF", f"{calc_path} is not an ELF binary"


def test_configure_is_executable_after_fix() -> None:
    configure_path = PROJECT_DIR / "configure"
    assert configure_path.exists(), "configure does not exist"

    file_stat = os.stat(configure_path)
    assert file_stat.st_mode & stat.S_IXUSR, "configure should be executable after the fix"


def test_makefile_was_generated() -> None:
    assert (PROJECT_DIR / "Makefile").exists(), "configure did not generate Makefile"


def test_source_and_build_inputs_were_not_modified() -> None:
    for relative_path, expected_hash in EXPECTED_HASHES.items():
        actual_hash = _sha256(PROJECT_DIR / relative_path)
        assert actual_hash == expected_hash, f"{relative_path} content was modified"
