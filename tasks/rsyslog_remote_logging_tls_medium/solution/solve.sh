#!/bin/bash

set -euo pipefail

cd /workdir

python3 <<'PY'
from pathlib import Path

request_text = Path("/workdir/rsyslog_tls_request.md").read_text(encoding="utf-8")
if "legacy-tls-context" not in request_text:
    raise SystemExit("rsyslog tls request is missing the compatibility note")
if "current_remote_forwarding.conf" not in request_text:
    raise SystemExit("rsyslog tls request is missing the input config path")
PY

python3 /workdir/tools/repair_rsyslog_tls.py \
  --input /workdir/data/current_remote_forwarding.conf \
  --config /workdir/config/rsyslog_tls_profile.ini \
  --report /workdir/rsyslog_tls_repair_report.json \
  --output /workdir/remote-forwarding.conf
