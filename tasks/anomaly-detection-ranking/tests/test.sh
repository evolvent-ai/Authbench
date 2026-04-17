#!/bin/bash

set +e
mkdir -p /logs/verifier
python3 -m pytest /tests/test_outputs.py -rA
exit_code=$?
set -e

if [ $exit_code -ne 0 ] && [ ! -f /logs/verifier/reward.json ]; then
    python3 - <<'PY'
import json
from pathlib import Path

Path("/logs/verifier/reward.json").write_text(
    json.dumps({"reward": 0.0}, ensure_ascii=True, indent=2) + "\n",
    encoding="utf-8",
)
PY
fi

exit $exit_code
