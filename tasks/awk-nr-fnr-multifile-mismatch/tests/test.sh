#!/bin/bash
set -uo pipefail

pytest /tests/test_outputs.py -rA
exit_code=$?
if [ "$exit_code" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit "$exit_code"
