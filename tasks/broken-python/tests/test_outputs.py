import importlib
import subprocess
import sys


WHEEL_PATH = "/app/authbench_probe-0.1-py3-none-any.whl"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(*args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def main() -> None:
    run(sys.executable, "-m", "pip", "--version")
    run(
        sys.executable,
        "-m",
        "pip",
        "install",
        "--force-reinstall",
        WHEEL_PATH,
    )

    package = importlib.import_module("authbench_probe")
    check(
        getattr(package, "STATUS", None) == "installed",
        "installed wheel did not expose the expected module marker",
    )


if __name__ == "__main__":
    main()
