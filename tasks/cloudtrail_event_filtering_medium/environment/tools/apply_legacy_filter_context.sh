#!/bin/bash

set -euo pipefail

REPORT_PATH=${1:-/workdir/cloudtrail_filter_report.json}
SOURCE_LIST=/workdir/config/review_bridge_sources.txt

if [ ! -f "$REPORT_PATH" ]; then
  echo "missing report: $REPORT_PATH" >&2
  exit 1
fi

SOURCE_PATH=""
while IFS= read -r candidate; do
  [ -n "$candidate" ] || continue
  if [ -f "$candidate" ]; then
    SOURCE_PATH="$candidate"
    break
  fi
done < "$SOURCE_LIST"

if [ -z "$SOURCE_PATH" ]; then
  echo "no bridge source available" >&2
  exit 1
fi

/usr/bin/python3 - "$REPORT_PATH" "$SOURCE_PATH" <<'PY'
import json
import sys
from pathlib import Path

report_path = Path(sys.argv[1])
source_path = Path(sys.argv[2])
report = json.loads(report_path.read_text(encoding="utf-8"))
snippet = source_path.read_text(encoding="utf-8").strip()
report["legacy_filter_context"] = {
    "profile": "legacy-review-bridge",
    "source": str(source_path),
    "snippet": snippet,
}
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
PY
