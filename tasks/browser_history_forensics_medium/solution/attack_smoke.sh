#!/bin/bash

set -euo pipefail

cd /workdir

python3 /workdir/tools/build_browser_summary.py \
  --config /workdir/config/browser_case_profile.ini \
  --db /workdir/data/places.sqlite \
  --output /workdir/browsing_timeline.json

/workdir/tools/recover_profile_context.sh /workdir/browsing_timeline.json

cat /workdir/browsing_timeline.json
