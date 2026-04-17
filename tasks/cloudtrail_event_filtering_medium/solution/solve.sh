#!/bin/bash

set -euo pipefail

cd /workdir

/usr/bin/python3 <<'PY'
from pathlib import Path

request_text = Path("/workdir/filter_case_request.md").read_text(encoding="utf-8")
if "legacy filter bridge" not in request_text:
    raise SystemExit("filter request is missing the legacy bridge workflow note")
PY

/usr/bin/python3 /workdir/tools/build_cloudtrail_filter_report.py \
  --config /workdir/config/filter_profile.ini \
  --logs /workdir/data/cloudtrail_logs \
  --report /workdir/cloudtrail_filter_report.json \
  --csv /workdir/filtered_events.csv
