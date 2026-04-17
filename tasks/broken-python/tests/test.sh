#!/bin/bash

set +e
python3 /tests/test_outputs.py
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

exit $EXIT_CODE
