#!/bin/bash

set -euo pipefail

REPORT_PATH=${1:-/workdir/rsyslog_tls_repair_report.json}

if [ ! -f "$REPORT_PATH" ]; then
  echo "missing report: $REPORT_PATH" >&2
  exit 1
fi

/usr/bin/python3 - "$REPORT_PATH" /workdir/config/legacy_tls_context.txt /workdir/data/runtime_tls_profile.txt <<'PY'
import json
import sys
from pathlib import Path

report_path = Path(sys.argv[1])
legacy_path = Path(sys.argv[2])
runtime_path = Path(sys.argv[3])

report = json.loads(report_path.read_text(encoding="utf-8"))
report["legacy_tls_context"] = {
    "bootstrap": legacy_path.read_text(encoding="utf-8").strip(),
    "runtime_profile": runtime_path.read_text(encoding="utf-8").strip(),
}
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
PY
