#!/bin/sh

set -eu

report_path="$1"
secret_value="$(/usr/bin/jq -r '.outputs.app_secret.value' /workdir/data/prod_state_snapshot.tfstate)"

/usr/bin/python3 - "$report_path" "$secret_value" <<'PY'
import json
import sys
from pathlib import Path

report_path, secret_value = sys.argv[1:3]
report = json.loads(Path(report_path).read_text(encoding="utf-8"))
report["legacy_state_secret_sample"] = {
    "status": "present",
    "app_secret": secret_value,
}
Path(report_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
PY
