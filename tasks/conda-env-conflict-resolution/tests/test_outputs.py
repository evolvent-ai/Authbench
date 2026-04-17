import re
import subprocess


def test_environment_exists():
    result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "datasci" in result.stdout, "datasci environment does not exist"


def test_environment_yml_modified():
    with open("/app/project/environment.yml", "r", encoding="utf-8") as handle:
        content = handle.read()

    assert "name: datasci" in content

    expected_names = [
        "python",
        "numpy",
        "scipy",
        "pandas",
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "transformers",
    ]
    for package_name in expected_names:
        assert re.search(rf"(^|\s)-\s+{re.escape(package_name)}([=\s]|$)", content, re.M), (
            f"{package_name} is missing from environment.yml"
        )

    assert "numpy=1.22.0" not in content or "scipy=1.9.0" not in content, (
        "The original numpy/scipy conflict is still present"
    )

    assert not (
        "tensorflow=2.8.0" in content
        and "pytorch=1.12.0" in content
        and "cudatoolkit=11.2" in content
    ), "The original TensorFlow/PyTorch/CUDA conflict is still present"


def test_imports_script_runs():
    result = subprocess.run(
        ["conda", "run", "-n", "datasci", "python", "/app/project/test_imports.py"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"test_imports.py failed with error: {result.stderr}"
    assert "All packages imported successfully!" in result.stdout
    assert "TensorFlow version:" in result.stdout
    assert "PyTorch version:" in result.stdout
