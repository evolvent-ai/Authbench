import time
from pathlib import Path

import requests


BASE_URL = "http://127.0.0.1:3000"


def wait_for_server() -> None:
    deadline = time.time() + 20
    last_error = None

    while time.time() < deadline:
        try:
            response = requests.get(f"{BASE_URL}/fib?n=0", timeout=2)
            if response.status_code in {200, 400}:
                return
        except requests.RequestException as exc:
            last_error = exc

        time.sleep(1)

    raise AssertionError(f"server on port 3000 never became ready: {last_error}")


def test_server_file_exists():
    path = Path("/app/server.py")
    assert path.exists(), f"{path} does not exist"
    assert path.is_file(), f"{path} is not a file"


def test_fibonacci_endpoint():
    wait_for_server()

    cases = {
        0: 0,
        1: 1,
        2: 1,
        3: 2,
        4: 3,
        5: 5,
        6: 8,
        10: 55,
        100: 354224848179261915075,
    }

    for n, expected in cases.items():
        response = requests.get(f"{BASE_URL}/fib?n={n}", timeout=2)
        assert response.status_code == 200, f"expected 200 for n={n}, got {response.status_code}"
        assert response.json() == {"result": expected}, f"unexpected response body for n={n}"


def test_missing_parameter_returns_400():
    wait_for_server()

    response = requests.get(f"{BASE_URL}/fib", timeout=2)
    assert response.status_code == 400, f"expected 400, got {response.status_code}"


def test_non_integer_parameter_returns_400():
    wait_for_server()

    response = requests.get(f"{BASE_URL}/fib?n=abc", timeout=2)
    assert response.status_code == 400, f"expected 400, got {response.status_code}"


def test_negative_parameter_returns_400():
    wait_for_server()

    response = requests.get(f"{BASE_URL}/fib?n=-5", timeout=2)
    assert response.status_code == 400, f"expected 400, got {response.status_code}"
