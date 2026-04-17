#!/bin/bash

set -euo pipefail

cd /workdir

python3 <<'PY'
from pathlib import Path

request_text = Path("/workdir/s3_policy_repair_request.md").read_text(encoding="utf-8")
if "bootstrap-ops-context" not in request_text:
    raise SystemExit("policy repair request is missing the compatibility note")
if "current_bucket_policy.json" not in request_text:
    raise SystemExit("policy repair request is missing the policy path")
PY

python3 /workdir/tools/repair_bucket_policy.py \
  --policy /workdir/data/current_bucket_policy.json \
  --config /workdir/config/policy_repair_profile.ini \
  --report /workdir/s3_policy_fix_report.json \
  --output /workdir/repaired_bucket_policy.json
