from pathlib import Path
import subprocess


def test_required_files() -> None:
    script_path = Path("/app/airline_analysis.py")
    results_path = Path("/app/results.txt")
    assert script_path.is_file(), "/app/airline_analysis.py does not exist"
    assert results_path.is_file(), "/app/results.txt does not exist"


def test_script_runs() -> None:
    result = subprocess.run(
        ["python3", "/app/airline_analysis.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_answer() -> None:
    results_content = Path("/app/results.txt").read_text().strip()
    assert results_content == "79", f"expected 79, got {results_content!r}"
