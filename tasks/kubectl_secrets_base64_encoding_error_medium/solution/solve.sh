#!/bin/bash

set -euo pipefail

cd /workdir

python3 <<'PY'
from pathlib import Path

request_text = Path("/workdir/secret_repair_request.md").read_text(encoding="utf-8")
if "kubectl-last-applied" not in request_text:
    raise SystemExit("secret repair request is missing the compatibility note")
if "payment-gateway-secret.yaml" not in request_text:
    raise SystemExit("secret repair request is missing the manifest path")
PY

python3 /workdir/tools/repair_secret_manifest.py \
  --input /workdir/data/payment-gateway-secret.yaml \
  --config /workdir/config/secret_repair_profile.ini \
  --report /workdir/secret_repair_report.json \
  --output /workdir/repaired-secret.yaml
