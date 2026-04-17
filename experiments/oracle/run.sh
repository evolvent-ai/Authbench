#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd -P)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd -P)
cd "$ROOT_DIR"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/params.env"

if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

echo "==> materializing oracle plan at $PLAN_DIR"
uv run authbench oracle-plan \
  "$TASKS_ROOT" \
  --plan-dir "$PLAN_DIR" \
  --job-name "$JOB_NAME" \
  --n-attempts "$N_ATTEMPTS" \
  --n-concurrent-trials "$N_CONCURRENT_TRIALS" \
  --jobs-dir "$JOBS_DIR"

if [ "$RUN_HARBOR" != "1" ]; then
  echo "==> skipping Harbor run because RUN_HARBOR=$RUN_HARBOR"
  exit 0
fi

harbor_args=()
if [ "$NO_DELETE" = "1" ]; then
  harbor_args+=(--no-delete)
fi

echo "==> running Harbor job from $PLAN_DIR/job.yaml"
uv run harbor run -c "$PLAN_DIR/job.yaml" "${harbor_args[@]}"
