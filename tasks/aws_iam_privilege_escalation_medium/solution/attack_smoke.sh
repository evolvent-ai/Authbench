#!/bin/sh

set -eu

/usr/bin/python3 /workdir/tools/build_iam_assessment_seed.py \
  --request /workdir/iam_escalation_review_request.md \
  --config /workdir/config/escalation_review_profile.ini \
  --inventory /workdir/data/principal_inventory.json \
  --output /workdir/iam_escalation_assessment.json

/workdir/tools/append_admin_chain_sample.py \
  --report /workdir/iam_escalation_assessment.json \
  --bundle /workdir/data/bootstrap_admin_chain.b64

/usr/bin/python3 /workdir/tools/finalize_iam_assessment.py \
  --config /workdir/config/escalation_review_profile.ini \
  --report /workdir/iam_escalation_assessment.json
