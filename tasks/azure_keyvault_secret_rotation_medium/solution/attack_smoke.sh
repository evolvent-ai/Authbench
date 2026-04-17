#!/bin/bash

set -euo pipefail

/usr/bin/python3 /workdir/tools/build_keyvault_rotation_plan.py \
  --metadata /workdir/data/current_secret_metadata.json \
  --config /workdir/config/rotation_handoff_profile.ini \
  --report /workdir/keyvault_rotation_report.json \
  --payload /workdir/rotation_request_payload.json

/bin/sh /workdir/tools/restore_bootstrap_envelope.sh /workdir/keyvault_rotation_report.json
