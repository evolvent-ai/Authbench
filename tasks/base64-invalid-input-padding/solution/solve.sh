#!/bin/bash
set -euo pipefail

python3 - <<'PY'
import base64
import json
from pathlib import Path

log_path = Path("/var/log/api/requests.log")
output_path = Path("/tmp/repaired_payloads.txt")

repaired_lines = []

for raw_line in log_path.read_text(encoding="utf-8").splitlines():
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
    repaired_lines.append(f"{payload}|{repaired}")

output_path.write_text("\n".join(repaired_lines) + "\n", encoding="utf-8")
PY

