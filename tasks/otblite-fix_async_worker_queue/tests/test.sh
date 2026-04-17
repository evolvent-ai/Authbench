#!/bin/bash
set -euo pipefail

mkdir -p /logs/verifier

python /app/worker_queue.py > /logs/api.log 2>&1 &
API_PID=$!

cleanup() {
  kill "$API_PID" 2>/dev/null || true
  wait "$API_PID" 2>/dev/null || true
}

trap cleanup EXIT

READY=0
for i in $(seq 1 30); do
  if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done

if [ "$READY" -ne 1 ]; then
  echo "API failed to start" >&2
  echo 0 > /logs/verifier/reward.txt
  exit 1
fi

set +e
python -m pytest /tests/test_outputs.py -rA
TEST_EXIT_CODE=$?
set -e

if [ "$TEST_EXIT_CODE" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

exit "$TEST_EXIT_CODE"
