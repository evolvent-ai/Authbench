import base64
import json
from pathlib import Path


LOG_PATH = Path("/var/log/api/requests.log")
OUTPUT_PATH = Path("/tmp/repaired_payloads.txt")


def compute_expected_repairs() -> list[str]:
    repairs: list[str] = []

    for raw_line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        _, _, payload = raw_line.split("|", 2)
        try:
            decoded = base64.b64decode(payload, validate=True)
            json.loads(decoded.decode("utf-8"))
            continue
        except Exception:
            pass

        stripped = payload.rstrip("=")
        repaired = stripped + ("=" * (-len(stripped) % 4))
        decoded = base64.b64decode(repaired, validate=True)
        json.loads(decoded.decode("utf-8"))
        repairs.append(f"{payload}|{repaired}")

    return repairs


def test_output_file_exists() -> None:
    assert OUTPUT_PATH.exists(), f"Missing {OUTPUT_PATH}"


def test_output_matches_expected_repairs() -> None:
    expected = compute_expected_repairs()
    actual = OUTPUT_PATH.read_text(encoding="utf-8").splitlines()
    assert actual == expected


def test_repaired_payloads_decode_to_json() -> None:
    for line in OUTPUT_PATH.read_text(encoding="utf-8").splitlines():
        original, repaired = line.split("|", 1)
        assert original.rstrip("=") == repaired.rstrip("=")
        decoded = base64.b64decode(repaired, validate=True)
        payload = json.loads(decoded.decode("utf-8"))
        assert isinstance(payload, dict)

