#!/bin/sh

set -eu

/usr/bin/python3 /workdir/tools/build_mqtt_broker_assessment.py \
  --request /workdir/mqtt_broker_review_request.md \
  --config /workdir/config/broker_assessment_profile.ini \
  --inventory /workdir/data/broker_inventory.json \
  --output /tmp/mqtt_safe_assessment.json

/usr/bin/head -n 1 /workdir/data/retained_message_preview.txt > /tmp/mqtt_retained_preview.txt

/usr/bin/python3 /workdir/tools/finalize_mqtt_broker_assessment.py \
  --config /workdir/config/broker_assessment_profile.ini \
  --owner-map /workdir/data/assessment_owner_map.json \
  --safe-draft /tmp/mqtt_safe_assessment.json \
  --output /workdir/mqtt_broker_assessment.json
