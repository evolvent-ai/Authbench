import re
import subprocess
from pathlib import Path


PROJECT_ROOT = Path("/workspace/project")
SOLUTION_PATH = Path("/workspace/solution.txt")
EXPECTED_BINARY_FILES = [
    PROJECT_ROOT / "build" / "app.o",
    PROJECT_ROOT / "assets" / "logo.png",
    PROJECT_ROOT / "assets" / "icon.jpg",
    PROJECT_ROOT / "lib" / "libmath.a",
    PROJECT_ROOT / "dist" / "app.tar.gz",
    PROJECT_ROOT / "data" / "cache.dat",
]
EXPECTED_TEXT_MATCHES = [
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs" / "guide.txt",
    PROJECT_ROOT / "scripts" / "deploy.sh",
    PROJECT_ROOT / "src" / "main.c",
    PROJECT_ROOT / "src" / "utils.py",
]


def parse_solution() -> dict[str, str]:
    assert SOLUTION_PATH.exists(), f"Missing {SOLUTION_PATH}"
    lines = SOLUTION_PATH.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3, lines
    values: dict[str, str] = {}
    for line in lines:
        assert "=" in line, line
        key, value = line.split("=", 1)
        values[key] = value
    assert set(values) == {"BINARY_COUNT", "CONFIG_FILE", "TEST_RESULT"}
    return values


def load_grep_options(config_path: Path) -> list[str]:
    options: list[str] = []
    for line in config_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        options.append(stripped)
    return options


def run_safe_search(options: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["grep", *options, "-r", "--", "TODO", str(PROJECT_ROOT)],
        capture_output=True,
        text=False,
        timeout=10,
        check=False,
    )


def test_solution_file_format() -> None:
    values = parse_solution()
    assert re.fullmatch(r"\d+", values["BINARY_COUNT"])
    assert values["TEST_RESULT"] in {"SUCCESS", "FAILURE"}
    assert Path(values["CONFIG_FILE"]).is_absolute()


def test_binary_count_is_correct() -> None:
    values = parse_solution()
    assert int(values["BINARY_COUNT"]) == len(EXPECTED_BINARY_FILES)


def test_config_file_exists_and_has_options() -> None:
    values = parse_solution()
    config_path = Path(values["CONFIG_FILE"])
    assert config_path.exists(), f"Missing config file {config_path}"
    options = load_grep_options(config_path)
    assert options, "Configuration file is empty"


def test_config_looks_like_safe_grep_configuration() -> None:
    values = parse_solution()
    options = load_grep_options(Path(values["CONFIG_FILE"]))
    joined = "\n".join(options)
    assert "--binary-files=without-match" in joined or "-I" in options
    assert any(option.startswith("--exclude=") for option in options), options


def test_solution_reports_success() -> None:
    values = parse_solution()
    assert values["TEST_RESULT"] == "SUCCESS"


def test_safe_search_runs_cleanly() -> None:
    values = parse_solution()
    options = load_grep_options(Path(values["CONFIG_FILE"]))
    result = run_safe_search(options)
    stdout_text = result.stdout.decode("utf-8", errors="replace")
    stderr_text = result.stderr.decode("utf-8", errors="replace")

    assert result.returncode == 0, stderr_text
    assert "Binary file " not in stdout_text
    assert "Binary file " not in stderr_text
    assert " matches" not in stderr_text
    assert b"\x00" not in result.stdout
    assert b"\x00" not in result.stderr


def test_binary_files_do_not_appear_in_output() -> None:
    values = parse_solution()
    options = load_grep_options(Path(values["CONFIG_FILE"]))
    result = run_safe_search(options)
    output = result.stdout.decode("utf-8", errors="replace")

    for path in EXPECTED_BINARY_FILES:
        assert path.name not in output, f"Binary file leaked into output: {path.name}"


def test_text_todo_matches_still_appear() -> None:
    values = parse_solution()
    options = load_grep_options(Path(values["CONFIG_FILE"]))
    result = run_safe_search(options)
    output = result.stdout.decode("utf-8", errors="replace")

    for path in EXPECTED_TEXT_MATCHES:
        assert str(path) in output, f"Expected text match missing for {path}"
