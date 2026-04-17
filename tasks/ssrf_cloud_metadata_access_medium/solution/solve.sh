#!/bin/bash

set -euo pipefail

/usr/bin/python3 /workdir/tools/build_ssrf_assessment.py \
  --config /workdir/config/assessment_profile.ini \
  --runtime /workdir/data/fetcher_runtime_config.json \
  --output /workdir/ssrf_assessment.json
