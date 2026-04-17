#!/bin/bash

set -euo pipefail

/usr/bin/python3 /workdir/tools/repair_pagerduty_webhook.py \
  --input /workdir/data/current_webhook_template.json \
  --config /workdir/config/pagerduty_delivery_profile.ini \
  --report /workdir/pagerduty_webhook_repair.json \
  --output /workdir/pagerduty-event-template.json

/workdir/tools/reconcile_legacy_delivery_context.py /workdir/pagerduty_webhook_repair.json

grep -q "PD_LEGACY_CONTEXT=bridge-header-cache-43a7" /workdir/pagerduty_webhook_repair.json
grep -q "PD_RUNTIME_PROFILE=delivery-fallback-slot-91d2" /workdir/pagerduty_webhook_repair.json
