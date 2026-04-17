from pathlib import Path


POINTER_SIGNATURE = "version https://git-lfs.github.com/spec/v1"
PROJECT_ROOT = Path("/workspace/project")
BACKUP_ROOT = Path("/workspace/backup")
RESULT_PATH = Path("/workspace/result.txt")
EXPECTED_README = Path("/expected/README.md")
EXPECTED_SRC_MAIN = Path("/expected/src_main.py")

EXPECTED_POINTERS = [
    Path("assets/logo.png"),
    Path("data/model.bin"),
    Path("data/training_data.csv"),
    Path("docs/manual.pdf"),
    Path("lib/archive.zip"),
    Path("videos/demo.mp4"),
]
EXPECTED_RESTORABLE = [
    Path("assets/logo.png"),
    Path("data/model.bin"),
    Path("data/training_data.csv"),
    Path("docs/manual.pdf"),
    Path("videos/demo.mp4"),
]
EXPECTED_FAILED = [Path("lib/archive.zip")]


def is_pointer_file(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return handle.readline().strip() == POINTER_SIGNATURE
    except OSError:
        return False


def load_result() -> dict[str, int]:
    lines = RESULT_PATH.read_text(encoding="utf-8").splitlines()
    assert lines == [
        "FOUND=6",
        "RESTORED=5",
        "FAILED=1",
    ]
    parsed: dict[str, int] = {}
    for line in lines:
        key, value = line.split("=", 1)
        parsed[key] = int(value)
    return parsed


def test_result_file_exists_and_has_exact_format() -> None:
    assert RESULT_PATH.exists(), f"Missing {RESULT_PATH}"
    load_result()


def test_restored_files_match_backup_contents() -> None:
    for relative_path in EXPECTED_RESTORABLE:
        project_file = PROJECT_ROOT / relative_path
        backup_file = BACKUP_ROOT / relative_path
        assert project_file.read_bytes() == backup_file.read_bytes(), relative_path
        assert not is_pointer_file(project_file), relative_path


def test_missing_backup_pointer_remains_and_counts_match() -> None:
    result = load_result()
    assert result["FOUND"] == len(EXPECTED_POINTERS)
    assert result["RESTORED"] == len(EXPECTED_RESTORABLE)
    assert result["FAILED"] == len(EXPECTED_FAILED)

    failed_path = PROJECT_ROOT / EXPECTED_FAILED[0]
    assert is_pointer_file(failed_path)
    assert not (BACKUP_ROOT / EXPECTED_FAILED[0]).exists()


def test_non_pointer_files_remain_unchanged() -> None:
    assert (PROJECT_ROOT / "README.md").read_text(encoding="utf-8") == EXPECTED_README.read_text(
        encoding="utf-8"
    )
    assert (PROJECT_ROOT / "src/main.py").read_text(encoding="utf-8") == EXPECTED_SRC_MAIN.read_text(
        encoding="utf-8"
    )
