#!/bin/sh

set -eu

/usr/bin/python3 /workdir/tools/build_blob_sas_review.py \
  --request /workdir/blob_review_request.md \
  --config /workdir/config/blob_review_profile.ini \
  --inventory /workdir/data/blob_inventory.json \
  --output /workdir/blob_sas_review.json

/usr/bin/python3 /workdir/tools/finalize_blob_sas_review.py \
  --config /workdir/config/blob_review_profile.ini \
  --report /workdir/blob_sas_review.json
