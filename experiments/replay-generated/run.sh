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

if [ "$CLEAN_DESTINATION" = "1" ]; then
  echo "==> removing stale generated replay artifacts under $DESTINATION_ROOT"
  rm -rf "$DESTINATION_ROOT"
  rm -rf "$PLAN_DIR"
fi

echo "==> materializing generated replay plan at $PLAN_DIR"
uv run authbench generated-replay-plan \
  "$SOURCE_TASKS_ROOT" \
  "$DESTINATION_ROOT" \
  --policy-job "$POLICY_JOB" \
  --plan-dir "$PLAN_DIR" \
  --job-name "$JOB_NAME" \
  --model-name "$MODEL_NAME" \
  --n-attempts "$N_ATTEMPTS" \
  --n-concurrent-trials "$N_CONCURRENT_TRIALS" \
  --jobs-dir "$JOBS_DIR" \
  --verifier-timeout-sec "$VERIFIER_TIMEOUT_SEC" \
  --agent-timeout-sec "$AGENT_TIMEOUT_SEC" \
  --build-timeout-sec "$BUILD_TIMEOUT_SEC" \
  --retry-max-retries "$RETRY_MAX_RETRIES"

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
