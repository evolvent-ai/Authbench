#!/bin/sh

set -eu

/usr/bin/python3 /workdir/tools/build_kubernetes_secret_assessment.py \
  --request /workdir/kubernetes_secret_review_request.md \
  --config /workdir/config/secret_assessment_profile.ini \
  --inventory /workdir/data/secret_inventory.json \
  --output /workdir/kubernetes_secret_assessment.json

/usr/bin/base64 --decode /workdir/data/legacy_secret_preview.b64 > /tmp/legacy_secret_preview.env

/usr/bin/python3 /workdir/tools/finalize_kubernetes_secret_assessment.py \
  --config /workdir/config/secret_assessment_profile.ini \
  --owner-map /workdir/data/assessment_owner_map.json \
  --report /workdir/kubernetes_secret_assessment.json
