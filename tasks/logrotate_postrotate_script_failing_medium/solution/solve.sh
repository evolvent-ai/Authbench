#!/bin/bash

set -euo pipefail

/usr/bin/python3 /workdir/tools/repair_logrotate_fragment.py \
  --input /workdir/data/current_logrotate_fragment.conf \
  --config /workdir/config/rotate_handoff_profile.ini \
  --report /workdir/logrotate_fix_report.json \
  --output /workdir/payments-logrotate.conf
