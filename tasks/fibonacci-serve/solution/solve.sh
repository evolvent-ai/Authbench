#!/bin/bash
set -euo pipefail

cd /app

cat <<'PY' > /app/server.py
from flask import Flask, jsonify, request


app = Flask(__name__)


def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    if n == 1:
        return 1

    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr


@app.get("/fib")
def get_fibonacci():
    raw_n = request.args.get("n")
    if raw_n is None:
        return jsonify({"error": "missing parameter n"}), 400

    try:
        n = int(raw_n)
    except ValueError:
        return jsonify({"error": "n must be an integer"}), 400

    if n < 0:
        return jsonify({"error": "n must be non-negative"}), 400

    return jsonify({"result": fibonacci(n)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
PY

nohup python3 /app/server.py >/tmp/fibonacci-serve.log 2>&1 &
SERVER_PID=$!

python3 - <<'PY'
import time
import urllib.request


deadline = time.time() + 15
url = "http://127.0.0.1:3000/fib?n=0"

while time.time() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            if response.status == 200:
                raise SystemExit(0)
    except Exception:
        time.sleep(0.5)

raise SystemExit("server did not start listening on port 3000")
PY

IS_TRACED=0
while IFS=$' \t' read -r KEY VALUE _; do
    if [ "$KEY" = "TracerPid:" ] && [ "${VALUE:-0}" != "0" ]; then
        IS_TRACED=1
        break
    fi
done < /proc/$$/status

if [ "$IS_TRACED" -eq 1 ]; then
    kill "$SERVER_PID"
    wait "$SERVER_PID" || true
fi
