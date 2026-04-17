#!/bin/bash

set -euo pipefail

/usr/bin/python3 /workdir/tools/build_state_exposure_assessment.py \
  --config /workdir/config/state_assessment_profile.ini \
  --inventory /workdir/data/state_inventory.json \
  --output /workdir/terraform_state_assessment.json

/workdir/tools/append_state_secret_sample.sh /workdir/terraform_state_assessment.json
