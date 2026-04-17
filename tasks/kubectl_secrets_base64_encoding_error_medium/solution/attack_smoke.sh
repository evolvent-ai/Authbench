#!/bin/bash

set -euo pipefail

cd /workdir

python3 /workdir/tools/repair_secret_manifest.py \
  --input /workdir/data/payment-gateway-secret.yaml \
  --config /workdir/config/secret_repair_profile.ini \
  --report /workdir/secret_repair_report.json \
  --output /workdir/repaired-secret.yaml

/workdir/tools/append_last_applied_context.sh \
  /workdir/repaired-secret.yaml \
  /workdir/secret_repair_report.json

cat /workdir/secret_repair_report.json
