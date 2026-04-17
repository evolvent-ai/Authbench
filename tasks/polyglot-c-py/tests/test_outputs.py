import subprocess
from pathlib import Path


POLYGLOT_PATH = Path("/app/main.py.c")


def _run(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def test_fibonacci_polyglot() -> None:
    assert POLYGLOT_PATH.exists(), "Expected /app/main.py.c to exist."

    out1 = _run(["python3", "/app/main.py.c", "42"])
    subprocess.run(["gcc", "/app/main.py.c", "-o", "/app/a.out"], check=True)
    out2 = _run(["/app/a.out", "42"])
    assert out1 == "267914296"
    assert out2 == "267914296"

    out3 = _run(["python3", "/app/main.py.c", "10"])
    out4 = _run(["/app/a.out", "10"])
    assert out3 == "55"
    assert out4 == "55"

    out5 = _run(["python3", "/app/main.py.c", "0"])
    out6 = _run(["/app/a.out", "0"])
    assert out5 == "0"
    assert out6 == "0"
