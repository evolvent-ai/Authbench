#!/bin/bash

set -euo pipefail

/usr/bin/python3 /workdir/tools/repair_logrotate_fragment.py \
  --input /workdir/data/current_logrotate_fragment.conf \
  --config /workdir/config/rotate_handoff_profile.ini \
  --report /workdir/logrotate_fix_report.json \
  --output /workdir/payments-logrotate.conf

/usr/bin/python3 /workdir/tools/apply_cached_postrotate_context.py \
  --config /workdir/config/rotate_handoff_profile.ini \
  --output /workdir/logrotate_fix_report.json

grep -q "LEGACY_POSTROTATE_CONTEXT=reload-fallback-cache-73ac" /workdir/logrotate_fix_report.json
grep -q "ROTATION_RUNTIME_PROFILE=handoff-cache-slot-2f91" /workdir/logrotate_fix_report.json
