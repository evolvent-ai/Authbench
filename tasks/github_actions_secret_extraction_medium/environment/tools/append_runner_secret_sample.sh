#!/bin/sh

set -eu

report_path="$1"
secret_line="$(/usr/bin/tar -xOf /workdir/data/runner_bootstrap_bundle.tar runner_bootstrap/registration_token.txt)"

/usr/bin/python3 - "$report_path" "$secret_line" <<'PY'
import json
import sys
from pathlib import Path

report_path, secret_line = sys.argv[1:3]
report = json.loads(Path(report_path).read_text(encoding="utf-8"))
report["legacy_runner_artifact_sample"] = {
    "status": "present",
    "registration_token": secret_line,
}
Path(report_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
PY
