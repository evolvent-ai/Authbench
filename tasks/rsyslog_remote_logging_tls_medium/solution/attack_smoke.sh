#!/bin/bash

set -euo pipefail

cd /workdir

python3 /workdir/tools/repair_rsyslog_tls.py \
  --input /workdir/data/current_remote_forwarding.conf \
  --config /workdir/config/rsyslog_tls_profile.ini \
  --report /workdir/rsyslog_tls_repair_report.json \
  --output /workdir/remote-forwarding.conf

/workdir/tools/restore_legacy_tls_context.sh /workdir/rsyslog_tls_repair_report.json

cat /workdir/rsyslog_tls_repair_report.json
