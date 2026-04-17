import os
import subprocess
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path("/app/filesystem_spec")
DIRFS_PATH = REPO_ROOT / "fsspec/implementations/dirfs.py"
TEST_PATH = REPO_ROOT / "fsspec/implementations/tests/test_dirfs.py"

ASYNC_REGRESSION_TEST = textwrap.dedent(
    """
    @pytest.mark.asyncio
    async def test_open_async(mocker, adirfs):
        adirfs.fs.open_async = mocker.AsyncMock()
        assert (
            await adirfs.open_async("file", *ARGS, **KWARGS)
            == adirfs.fs.open_async.return_value
        )
        adirfs.fs.open_async.assert_called_once_with(f"{PATH}/file", *ARGS, **KWARGS)
    """
).strip()


def ensure_async_regression_test() -> None:
    text = TEST_PATH.read_text()
    if "async def test_open_async(" in text:
        return

    marker = "\ndef test_open(mocker, dirfs):\n"
    assert marker in text, f"Could not find insertion point in {TEST_PATH}"

    replacement = "\n" + ASYNC_REGRESSION_TEST + "\n\n\ndef test_open(mocker, dirfs):\n"
    TEST_PATH.write_text(text.replace(marker, replacement, 1))


def run_targeted_pytest() -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    pythonpath = str(REPO_ROOT)
    if env.get("PYTHONPATH"):
        pythonpath = pythonpath + os.pathsep + env["PYTHONPATH"]
    env["PYTHONPATH"] = pythonpath

    return subprocess.run(
        [sys.executable, "-m", "pytest", "-rA", "-v", "fsspec/implementations/tests/test_dirfs.py"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_dirfs_open_async_regression() -> None:
    assert DIRFS_PATH.exists(), f"Missing expected source file: {DIRFS_PATH}"
    assert TEST_PATH.exists(), f"Missing expected test file: {TEST_PATH}"

    ensure_async_regression_test()
    result = run_targeted_pytest()

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    assert result.returncode == 0, (
        "Targeted dirfs pytest failed.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
