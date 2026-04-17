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

skipped_required_tasks=()

is_task_dir() {
  local candidate=$1
  [ -f "$candidate/instruction.md" ] &&
    [ -f "$candidate/task.toml" ] &&
    [ -d "$candidate/environment" ] &&
    [ -d "$candidate/solution" ] &&
    [ -d "$candidate/tests" ]
}

list_task_dirs() {
  local root=$1
  if [ ! -d "$root" ]; then
    return 1
  fi
  if is_task_dir "$root"; then
    (cd "$root" && pwd -P)
    return 0
  fi

  find "$root" -mindepth 1 -maxdepth 1 -type d | sort | while IFS= read -r candidate; do
    if is_task_dir "$candidate"; then
      (cd "$candidate" && pwd -P)
    fi
  done
}

replay_spec_supported() {
  local task_dir=$1
  python3 - "$task_dir" <<'PY'
import json
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
spec_path = task_dir / "tests" / "permission_eval_spec.json"
if not spec_path.is_file():
    print(
        f"{task_dir.name}: required replay skipped because permission_eval_spec.json is missing",
        file=sys.stderr,
    )
    raise SystemExit(1)

payload = json.loads(spec_path.read_text(encoding="utf-8"))
allowed = {"required_permissions", "scored_roots", "implicit_permissions", "sensitive_permissions"}
extra = sorted(set(payload) - allowed)
if extra:
    print(
        f"{task_dir.name}: required replay skipped because permission_eval_spec has unsupported keys: {', '.join(extra)}",
        file=sys.stderr,
    )
    raise SystemExit(1)
PY
}

write_required_policy() {
  local src_task=$1
  local output_path=$2
  uv run python - "$src_task" "$output_path" <<'PY'
import json
import sys
from pathlib import Path

from libs.authbench_sync.permission_eval_shared import (
    normalize_permission_eval_spec,
    permission_policy_to_payload,
)

task_dir = Path(sys.argv[1]).expanduser().resolve()
output_path = Path(sys.argv[2]).expanduser().resolve()
payload = json.loads((task_dir / "tests" / "permission_eval_spec.json").read_text(encoding="utf-8"))
spec = normalize_permission_eval_spec(payload)
payload = permission_policy_to_payload(spec.required_permissions)
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
PY
}

prepare_required_replay_tasks() {
  local -a source_tasks=()

  mapfile -t source_tasks < <(list_task_dirs "$SOURCE_TASKS_ROOT")
  if [ "${#source_tasks[@]}" -eq 0 ]; then
    echo "No source tasks found under: $SOURCE_TASKS_ROOT" >&2
    exit 1
  fi

  if [ "$CLEAN_DESTINATION" = "1" ]; then
    echo "==> removing stale required-permissions replay artifacts under $DESTINATION_ROOT"
    rm -rf "$DESTINATION_ROOT" "$PLAN_DIR"
  fi

  mkdir -p "$DESTINATION_ROOT" "$POLICY_ROOT"

  for src_task in "${source_tasks[@]}"; do
    local task_name replay_task required_policy
    task_name=$(basename "$src_task")
    replay_task="$DESTINATION_ROOT/${task_name}-${REQUIRED_REPLAY_TASK_SUFFIX}"
    required_policy="$POLICY_ROOT/${task_name}.json"

    if ! replay_spec_supported "$src_task"; then
      echo "==> skipping required replay bootstrap for $task_name"
      rm -rf "$replay_task" "$required_policy"
      skipped_required_tasks+=("$task_name")
      continue
    fi

    echo "==> materializing required policy for $task_name"
    write_required_policy "$src_task" "$required_policy"

    echo "==> syncing required-permissions replay task $replay_task"
    rm -rf "$replay_task"
    uv run authbench openclaw-replay-task-sync \
      "$src_task" \
      "$replay_task" \
      --policy-file "$required_policy" \
      --verifier-timeout-sec "$VERIFIER_TIMEOUT_SEC" \
      --agent-timeout-sec "$AGENT_TIMEOUT_SEC" \
      --build-timeout-sec "$BUILD_TIMEOUT_SEC"
  done

  if [ "${#skipped_required_tasks[@]}" -gt 0 ]; then
    echo "==> skipped required replay tasks: ${skipped_required_tasks[*]}"
  fi
}

prepare_required_replay_tasks

echo "==> required-permissions replay run"
echo "run_id=$RUN_ID"
echo "source_tasks_root=$SOURCE_TASKS_ROOT"
echo "destination_root=$DESTINATION_ROOT"
echo "policy_root=$POLICY_ROOT"
echo "job_name=$JOB_NAME"
echo "plan_dir=$PLAN_DIR"
echo "model_name=$MODEL_NAME"

echo "==> materializing required-permissions replay plan at $PLAN_DIR"
uv run authbench replay-plan \
  "$DESTINATION_ROOT" \
  --plan-dir "$PLAN_DIR" \
  --job-name "$JOB_NAME" \
  --model-name "$MODEL_NAME" \
  --n-attempts "$N_ATTEMPTS" \
  --n-concurrent-trials "$N_CONCURRENT_TRIALS" \
  --jobs-dir "$JOBS_DIR" \
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
