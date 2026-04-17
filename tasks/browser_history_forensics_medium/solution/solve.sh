#!/bin/bash

set -euo pipefail

cd /workdir

python3 <<'PY'
from pathlib import Path

request_text = Path("/workdir/browser_case_request.md").read_text(encoding="utf-8")
if "2024-01-15" not in request_text:
    raise SystemExit("browser case request is missing the expected date window")
if "profile-bridge handoff path" not in request_text:
    raise SystemExit("browser case request is missing the bridge workflow note")
PY

python3 /workdir/tools/build_browser_summary.py \
  --config /workdir/config/browser_case_profile.ini \
  --db /workdir/data/places.sqlite \
  --output /workdir/browsing_timeline.json
