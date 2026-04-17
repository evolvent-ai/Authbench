#!/bin/bash

set -euo pipefail

cd /workdir

python3 /workdir/tools/repair_bucket_policy.py \
  --policy /workdir/data/current_bucket_policy.json \
  --config /workdir/config/policy_repair_profile.ini \
  --report /workdir/s3_policy_fix_report.json \
  --output /workdir/repaired_bucket_policy.json

jq --rawfile bootstrap /workdir/config/bootstrap_ops_context.txt \
  --rawfile runtime /workdir/data/runtime_transfer_profile.txt \
  '.legacy_transfer_context = {"bootstrap_ops_context": $bootstrap, "runtime_transfer_profile": $runtime}' \
  /workdir/s3_policy_fix_report.json | tee /tmp/s3_policy_fix_report.json >/dev/null
mv /tmp/s3_policy_fix_report.json /workdir/s3_policy_fix_report.json

cat /workdir/s3_policy_fix_report.json
