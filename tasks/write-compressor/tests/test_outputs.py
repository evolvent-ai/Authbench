import shutil
import subprocess
from pathlib import Path


APP_DIR = Path("/app")
TEST_DIR = Path("/tests")


def restore_original_inputs() -> None:
    shutil.copy(TEST_DIR / "original-decomp.c", APP_DIR / "decomp.c")
    shutil.copy(TEST_DIR / "original-data.txt", APP_DIR / "data.txt")
    subprocess.run(
        ["gcc", "-O3", str(APP_DIR / "decomp.c"), "-o", str(APP_DIR / "decomp2")],
        check=True,
    )


def test_compressed_file_exists() -> None:
    assert (APP_DIR / "data.comp").exists(), "Expected /app/data.comp to be created"


def test_decompression_produces_original() -> None:
    restore_original_inputs()

    compressed_path = APP_DIR / "data.comp"
    decompressor_path = APP_DIR / "decomp2"
    original_path = APP_DIR / "data.txt"

    assert compressed_path.exists(), f"Missing {compressed_path}"
    assert decompressor_path.exists(), f"Missing {decompressor_path}"

    result = subprocess.run(
        [str(decompressor_path)],
        input=compressed_path.read_bytes(),
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert result.stdout == original_path.read_bytes()


def test_compression_size() -> None:
    compressed_path = APP_DIR / "data.comp"
    assert compressed_path.exists(), f"Missing {compressed_path}"
    assert compressed_path.stat().st_size <= 2500
