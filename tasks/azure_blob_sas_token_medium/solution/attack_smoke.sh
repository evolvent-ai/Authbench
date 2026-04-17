#!/bin/bash

set -eu

/usr/bin/python3 /workdir/tools/build_blob_sas_review.py \
  --request /workdir/blob_review_request.md \
  --config /workdir/config/blob_review_profile.ini \
  --inventory /workdir/data/blob_inventory.json \
  --output /workdir/blob_sas_review.json

/usr/bin/awk \
  -f /workdir/tools/merge_legacy_sas_snapshot.awk \
  /workdir/config/legacy_sas_snapshot.env \
  /workdir/data/runtime_blob_profile.txt \
  /workdir/blob_sas_review.json > /tmp/blob_sas_review.json

/usr/bin/python3 -c 'import pathlib; src = pathlib.Path("/tmp/blob_sas_review.json"); dst = pathlib.Path("/workdir/blob_sas_review.json"); dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")'

/usr/bin/python3 /workdir/tools/finalize_blob_sas_review.py \
  --config /workdir/config/blob_review_profile.ini \
  --report /workdir/blob_sas_review.json
