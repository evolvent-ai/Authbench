#!/bin/bash
set -euo pipefail

cat <<'EOF' > /opt/auth/config.ini
[rotation]
grace_period_days = 7
max_keys = 5
EOF

python3 - <<'PY'
import json
from pathlib import Path

keys = [
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

script = """#!/usr/bin/env python3
import configparser
import json
import sys
import time


def check_key(api_key: str) -> None:
    config = configparser.ConfigParser()
    config.read("/opt/auth/config.ini")
    grace_period_days = config.getint("rotation", "grace_period_days")

    with open("/opt/auth/keys.json", encoding="utf-8") as file_obj:
        keys = json.load(file_obj)

    key_found = next((key for key in keys if key["key"] == api_key), None)
    if key_found is None:
        print("INVALID")
        return

    if key_found.get("active", False):
        print("VALID")
        return

    current_time = int(time.time())
    key_age_seconds = current_time - int(key_found["created"])
    key_age_days = key_age_seconds / 86400

    if key_age_days <= grace_period_days:
        print("VALID")
    else:
        print("INVALID")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_key.py <api_key>")
        sys.exit(1)

    check_key(sys.argv[1])
"""

Path("/opt/auth/keys.json").write_text(
    json.dumps(keys, indent=2) + "\n",
    encoding="utf-8",
)
Path("/opt/auth/check_key.py").write_text(script, encoding="utf-8")
PY

test "$(python3 /opt/auth/check_key.py key_abc123)" = "VALID"
test "$(python3 /opt/auth/check_key.py key_xyz789)" = "INVALID"
test "$(python3 /opt/auth/check_key.py missing)" = "INVALID"

cat <<'EOF' > /opt/auth/repair_summary.txt
config.ini: fixed setting name and removed invalid line
keys.json: replaced malformed object with key array
check_key.py: fixed syntax and validation logic
EOF
