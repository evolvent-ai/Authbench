#!/bin/bash

set -euo pipefail

/usr/bin/python3 /workdir/tools/repair_pagerduty_webhook.py \
  --input /workdir/data/current_webhook_template.json \
  --config /workdir/config/pagerduty_delivery_profile.ini \
  --report /workdir/pagerduty_webhook_repair.json \
  --output /workdir/pagerduty-event-template.json
