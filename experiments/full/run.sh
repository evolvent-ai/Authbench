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

STAGES=${STAGES// /}
skipped_replay_tasks=()

has_stage() {
  if [ "$STAGES" = "all" ]; then
    return 0
  fi
  case ",$STAGES," in
    *,"$1",*) return 0 ;;
    *) return 1 ;;
  esac
}

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
    raise SystemExit(0)

payload = json.loads(spec_path.read_text(encoding="utf-8"))
allowed = {"required_permissions", "scored_roots", "implicit_permissions", "sensitive_permissions"}
extra = sorted(set(payload) - allowed)
if extra:
    print(
        f"{task_dir.name}: replay sync skipped because permission_eval_spec has unsupported keys: {', '.join(extra)}",
        file=sys.stderr,
    )
    raise SystemExit(1)
PY
}

prebuild_task_root() {
  local root=$1
  local -a task_dirs=()

  if [ ! -d "$root" ]; then
    return 0
  fi

  mapfile -t task_dirs < <(list_task_dirs "$root" || true)
  for task_dir in "${task_dirs[@]}"; do
    echo "==> prebuilding $task_dir"
    uv run authbench prebuild-task-image "$task_dir"
  done
}

run_harbor_plan() {
  local plan_dir=$1
  local harbor_args=()

  if [ "$RUN_HARBOR" != "1" ]; then
    echo "==> skipping Harbor run because RUN_HARBOR=$RUN_HARBOR"
    return 0
  fi
  if [ "$NO_DELETE" = "1" ]; then
    harbor_args+=(--no-delete)
  fi

  echo "==> running Harbor job from $plan_dir/job.yaml"
  uv run harbor run -c "$plan_dir/job.yaml" "${harbor_args[@]}"
}

prepare_generated_roots() {
  local -a source_tasks=()

  mapfile -t source_tasks < <(list_task_dirs "$SOURCE_TASKS_ROOT")
  if [ "${#source_tasks[@]}" -eq 0 ]; then
    echo "No source tasks found under: $SOURCE_TASKS_ROOT" >&2
    exit 1
  fi

  if [ "$CLEAN_PREPARED_ROOTS" = "1" ]; then
    echo "==> removing stale prepared task roots"
    rm -rf "$TASKS_GEN_ROOT" "$TASKS_REPLAY_ROOT"
  fi

  mkdir -p "$TASKS_GEN_ROOT" "$TASKS_REPLAY_ROOT"

  for src_task in "${source_tasks[@]}"; do
    local task_name permission_task replay_task
    task_name=$(basename "$src_task")
    permission_task="$TASKS_GEN_ROOT/${task_name}-${PERMISSION_TASK_SUFFIX}"
    replay_task="$TASKS_REPLAY_ROOT/${task_name}-${ALLOWALL_REPLAY_TASK_SUFFIX}"

    echo "==> syncing permission-gen task $permission_task"
    rm -rf "$permission_task"
    uv run authbench permission-gen-task-sync "$src_task" "$permission_task"

    if ! replay_spec_supported "$src_task"; then
      echo "==> skipping replay bootstrap for $task_name"
      rm -rf "$replay_task"
      skipped_replay_tasks+=("$task_name")
      continue
    fi

    echo "==> syncing allow-all replay task $replay_task"
    rm -rf "$replay_task"
    uv run authbench openclaw-replay-task-sync "$src_task" "$replay_task"
  done

  if [ "$PREBUILD_PREPARED_TASKS" = "1" ]; then
    prebuild_task_root "$TASKS_GEN_ROOT"
    prebuild_task_root "$TASKS_REPLAY_ROOT"
  fi
}

run_oracle_stage() {
  env \
    TASKS_ROOT="$SOURCE_TASKS_ROOT" \
    JOB_NAME="$ORACLE_JOB_NAME" \
    PLAN_DIR="$ORACLE_PLAN_DIR" \
    N_ATTEMPTS="$ORACLE_N_ATTEMPTS" \
    N_CONCURRENT_TRIALS="$ORACLE_N_CONCURRENT_TRIALS" \
    JOBS_DIR="$ORACLE_JOBS_DIR" \
    RUN_HARBOR="$RUN_HARBOR" \
    NO_DELETE="$NO_DELETE" \
    "$ROOT_DIR/experiments/oracle/run.sh"
}

run_permission_gen_stage() {
  env \
    TASKS_ROOT="$TASKS_GEN_ROOT" \
    JOB_NAME="$PERMISSION_GEN_JOB_NAME" \
    PLAN_DIR="$PERMISSION_GEN_PLAN_DIR" \
    MODEL_NAME="$PERMISSION_GEN_MODEL_NAME" \
    REASONING_EFFORT="$PERMISSION_GEN_REASONING_EFFORT" \
    N_ATTEMPTS="$PERMISSION_GEN_N_ATTEMPTS" \
    N_CONCURRENT_TRIALS="$PERMISSION_GEN_N_CONCURRENT_TRIALS" \
    JOBS_DIR="$PERMISSION_GEN_JOBS_DIR" \
    MAX_TURNS="$PERMISSION_GEN_MAX_TURNS" \
    RETRY_MAX_RETRIES="$RETRY_MAX_RETRIES" \
    RUN_HARBOR="$RUN_HARBOR" \
    NO_DELETE="$NO_DELETE" \
    "$ROOT_DIR/experiments/permission-gen/run.sh"
}

run_replay_allowall_stage() {
  env \
    TASKS_ROOT="$TASKS_REPLAY_ROOT" \
    JOB_NAME="$REPLAY_ALLOWALL_JOB_NAME" \
    PLAN_DIR="$REPLAY_ALLOWALL_PLAN_DIR" \
    MODEL_NAME="$REPLAY_MODEL_NAME" \
    N_ATTEMPTS="$REPLAY_ALLOWALL_N_ATTEMPTS" \
    N_CONCURRENT_TRIALS="$REPLAY_ALLOWALL_N_CONCURRENT_TRIALS" \
    JOBS_DIR="$REPLAY_ALLOWALL_JOBS_DIR" \
    RETRY_MAX_RETRIES="$RETRY_MAX_RETRIES" \
    RUN_HARBOR="$RUN_HARBOR" \
    NO_DELETE="$NO_DELETE" \
    "$ROOT_DIR/experiments/replay-allowall/run.sh"
}

run_generated_replay_stage() {
  if [ "$PREBUILD_GENERATED_REPLAY_TASKS" = "1" ]; then
    env \
      SOURCE_TASKS_ROOT="$SOURCE_TASKS_ROOT" \
      POLICY_JOB="$POLICY_JOB" \
      DESTINATION_ROOT="$GENERATED_REPLAY_ROOT" \
      PLAN_DIR="$GENERATED_REPLAY_PLAN_DIR" \
      JOB_NAME="$GENERATED_REPLAY_JOB_NAME" \
      MODEL_NAME="$REPLAY_MODEL_NAME" \
      N_ATTEMPTS="$GENERATED_REPLAY_N_ATTEMPTS" \
      N_CONCURRENT_TRIALS="$GENERATED_REPLAY_N_CONCURRENT_TRIALS" \
      JOBS_DIR="$GENERATED_REPLAY_JOBS_DIR" \
      VERIFIER_TIMEOUT_SEC="$VERIFIER_TIMEOUT_SEC" \
      AGENT_TIMEOUT_SEC="$AGENT_TIMEOUT_SEC" \
      BUILD_TIMEOUT_SEC="$BUILD_TIMEOUT_SEC" \
      RETRY_MAX_RETRIES="$RETRY_MAX_RETRIES" \
      CLEAN_DESTINATION="$CLEAN_GENERATED_REPLAY" \
      RUN_HARBOR=0 \
      NO_DELETE="$NO_DELETE" \
      "$ROOT_DIR/experiments/replay-generated/run.sh"
    prebuild_task_root "$GENERATED_REPLAY_ROOT"
    run_harbor_plan "$GENERATED_REPLAY_PLAN_DIR"
    return 0
  fi

  env \
    SOURCE_TASKS_ROOT="$SOURCE_TASKS_ROOT" \
    POLICY_JOB="$POLICY_JOB" \
    DESTINATION_ROOT="$GENERATED_REPLAY_ROOT" \
    PLAN_DIR="$GENERATED_REPLAY_PLAN_DIR" \
    JOB_NAME="$GENERATED_REPLAY_JOB_NAME" \
    MODEL_NAME="$REPLAY_MODEL_NAME" \
    N_ATTEMPTS="$GENERATED_REPLAY_N_ATTEMPTS" \
    N_CONCURRENT_TRIALS="$GENERATED_REPLAY_N_CONCURRENT_TRIALS" \
    JOBS_DIR="$GENERATED_REPLAY_JOBS_DIR" \
    VERIFIER_TIMEOUT_SEC="$VERIFIER_TIMEOUT_SEC" \
    AGENT_TIMEOUT_SEC="$AGENT_TIMEOUT_SEC" \
    BUILD_TIMEOUT_SEC="$BUILD_TIMEOUT_SEC" \
    RETRY_MAX_RETRIES="$RETRY_MAX_RETRIES" \
    CLEAN_DESTINATION="$CLEAN_GENERATED_REPLAY" \
    RUN_HARBOR="$RUN_HARBOR" \
    NO_DELETE="$NO_DELETE" \
    "$ROOT_DIR/experiments/replay-generated/run.sh"
}

echo "==> full experiment run"
echo "run_id=$RUN_ID"
echo "stages=$STAGES"
echo "source_tasks_root=$SOURCE_TASKS_ROOT"
echo "experiment_jobs_root=$EXPERIMENT_JOBS_ROOT"

if has_stage "oracle"; then
  run_oracle_stage
fi

if has_stage "prepare"; then
  prepare_generated_roots
fi

if has_stage "permission-gen"; then
  run_permission_gen_stage
fi

if has_stage "replay-allowall"; then
  run_replay_allowall_stage
fi

if has_stage "replay-generated"; then
  run_generated_replay_stage
fi

if [ "${#skipped_replay_tasks[@]}" -gt 0 ]; then
  printf 'Skipped replay bootstrap for legacy-spec tasks: %s\n' "${skipped_replay_tasks[*]}" >&2
fi
