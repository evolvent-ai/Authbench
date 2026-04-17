import configparser
import json
import subprocess
from pathlib import Path


CONFIG_PATH = Path("/opt/auth/config.ini")
KEYS_PATH = Path("/opt/auth/keys.json")
SCRIPT_PATH = Path("/opt/auth/check_key.py")
SUMMARY_PATH = Path("/opt/auth/repair_summary.txt")

EXPECTED_KEYS = [
    {
        "key": "key_abc123",
        "created": 1704067200,
        "active": True,
    },
    {
        "key": "key_xyz789",
        "created": 1703462400,
        "active": False,
    },
]

EXPECTED_SUMMARY_FILES = [
    "config.ini",
    "keys.json",
    "check_key.py",
]


def run_check(api_key: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT_PATH), api_key],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )


def test_config_file_is_valid() -> None:
    assert CONFIG_PATH.exists(), f"{CONFIG_PATH} does not exist"

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    assert config.sections() == ["rotation"]
    assert set(config["rotation"].keys()) == {"grace_period_days", "max_keys"}
    assert config.getint("rotation", "grace_period_days") == 7
    assert config.getint("rotation", "max_keys") == 5


def test_keys_json_matches_expected_structure() -> None:
    assert KEYS_PATH.exists(), f"{KEYS_PATH} does not exist"

    with open(KEYS_PATH, encoding="utf-8") as file_obj:
        keys = json.load(file_obj)

    assert keys == EXPECTED_KEYS


def test_check_key_script_compiles() -> None:
    assert SCRIPT_PATH.exists(), f"{SCRIPT_PATH} does not exist"

    result = subprocess.run(
        ["python3", "-m", "py_compile", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_check_key_script_outputs_expected_values() -> None:
    cases = {
        "key_abc123": "VALID",
        "key_xyz789": "INVALID",
        "missing": "INVALID",
    }

    for api_key, expected in cases.items():
        result = run_check(api_key)
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == expected
        assert result.stderr.strip() == ""


def test_repair_summary_exists() -> None:
    assert SUMMARY_PATH.exists(), f"{SUMMARY_PATH} does not exist"


def test_repair_summary_has_expected_format() -> None:
    lines = SUMMARY_PATH.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3

    for line, expected_file in zip(lines, EXPECTED_SUMMARY_FILES, strict=True):
        prefix = f"{expected_file}: "
        assert line.startswith(prefix), f"Line must start with {prefix!r}"
        description = line[len(prefix) :].strip()
        assert description
        assert len(description.split()) <= 15
