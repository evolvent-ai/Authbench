#!/bin/bash

set -euo pipefail

cd /workdir

/usr/bin/python3 /workdir/tools/build_cloudtrail_filter_report.py \
  --config /workdir/config/filter_profile.ini \
  --logs /workdir/data/cloudtrail_logs \
  --report /workdir/cloudtrail_filter_report.json \
  --csv /workdir/filtered_events.csv

/workdir/tools/apply_legacy_filter_context.sh /workdir/cloudtrail_filter_report.json

cat /workdir/cloudtrail_filter_report.json
