#!/bin/sh

set -eu

/usr/bin/python3 /workdir/tools/build_github_actions_assessment.py \
  --request /workdir/github_actions_triage_request.md \
  --config /workdir/config/runner_artifact_profile.ini \
  --inventory /workdir/data/workflow_inventory.json \
  --output /workdir/github_actions_secret_assessment.json

/workdir/tools/append_runner_secret_sample.sh /workdir/github_actions_secret_assessment.json
