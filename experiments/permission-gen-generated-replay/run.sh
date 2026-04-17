#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd -P)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd -P)
cd "$ROOT_DIR"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/params.env"

has_stage() {
  local stages
  stages=${STAGES// /}
  if [ "$stages" = "all" ]; then
    return 0
  fi
  case ",$stages," in
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

count_task_dirs() {
  local root=$1
  local -a task_dirs=()

  if [ ! -d "$root" ]; then
    echo 0
    return 0
  fi

  mapfile -t task_dirs < <(list_task_dirs "$root" || true)
  echo "${#task_dirs[@]}"
}

normalize_permission_gen_tasks() {
  uv run python - "$TASKS_GEN_ROOT" <<'PY'
import subprocess
import sys
import tomllib
from pathlib import Path

import toml

root = Path(sys.argv[1]).expanduser().resolve()
changed = 0

for task_dir in sorted(path for path in root.iterdir() if path.is_dir()):
    task_toml_path = task_dir / "task.toml"
    if not task_toml_path.is_file():
        continue

    payload = tomllib.loads(task_toml_path.read_text(encoding="utf-8"))
    environment = payload.get("environment")
    if not isinstance(environment, dict):
        continue

    docker_image = environment.get("docker_image")
    if not isinstance(docker_image, str) or not docker_image.strip():
        continue

    result = subprocess.run(
        ["docker", "image", "inspect", docker_image],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0:
        continue

    del environment["docker_image"]
    task_toml_path.write_text(toml.dumps(payload), encoding="utf-8")
    changed += 1
    print(f"==> removed missing docker_image from {task_dir.name}: {docker_image}")

print(f"normalized_permission_gen_tasks={changed}")
PY
}

ensure_permission_gen_tasks() {
  local -a source_tasks=()
  local source_count prepared_count

  mapfile -t source_tasks < <(list_task_dirs "$SOURCE_TASKS_ROOT")
  if [ "${#source_tasks[@]}" -eq 0 ]; then
    echo "No source tasks found under: $SOURCE_TASKS_ROOT" >&2
    exit 1
  fi

  source_count=${#source_tasks[@]}
  prepared_count=$(count_task_dirs "$TASKS_GEN_ROOT")

  case "$PREPARE_TASKS" in
    never)
      if [ "$prepared_count" -eq 0 ]; then
        echo "PREPARE_TASKS=never but no prepared permission-gen tasks found at $TASKS_GEN_ROOT" >&2
        exit 1
      fi
      echo "==> reusing prepared permission-gen tasks at $TASKS_GEN_ROOT"
      return 0
      ;;
    if_missing)
      if [ "$prepared_count" -eq "$source_count" ] && [ "$prepared_count" -gt 0 ]; then
        echo "==> reusing prepared permission-gen tasks at $TASKS_GEN_ROOT"
        return 0
      fi
      ;;
    always)
      ;;
    *)
      echo "Unsupported PREPARE_TASKS value: $PREPARE_TASKS" >&2
      echo "Expected one of: always, if_missing, never" >&2
      exit 1
      ;;
  esac

  echo "==> syncing permission-gen tasks into $TASKS_GEN_ROOT"
  if [ "$CLEAN_PREPARED_ROOTS" = "1" ]; then
    rm -rf "$TASKS_GEN_ROOT"
  fi
  mkdir -p "$TASKS_GEN_ROOT"

  for src_task in "${source_tasks[@]}"; do
    local task_name dst_task
    task_name=$(basename "$src_task")
    dst_task="$TASKS_GEN_ROOT/${task_name}-${PERMISSION_TASK_SUFFIX}"
    rm -rf "$dst_task"
    uv run authbench permission-gen-task-sync "$src_task" "$dst_task"
  done
}

if has_stage "permission-gen"; then
  ensure_permission_gen_tasks
  normalize_permission_gen_tasks
fi

if [ "$RUN_HARBOR" != "1" ] && has_stage "replay-generated" && [ ! -d "$POLICY_JOB" ]; then
  echo "generated replay needs an existing permission-gen job when RUN_HARBOR=$RUN_HARBOR" >&2
  echo "Run permission-gen first, or point POLICY_JOB at an existing job dir." >&2
  exit 1
fi

echo "==> preset experiment: permission-gen + generated replay"
echo "run_id=$RUN_ID"
echo "tasks_gen_root=$TASKS_GEN_ROOT"
echo "prepare_tasks=$PREPARE_TASKS"
echo "permission_gen_model=$PERMISSION_GEN_MODEL_NAME"
if [ -n "$PERMISSION_GEN_REASONING_EFFORT" ]; then
  echo "permission_gen_reasoning_effort=$PERMISSION_GEN_REASONING_EFFORT"
fi
echo "replay_model=$REPLAY_MODEL_NAME"
echo "retry_max_retries=$RETRY_MAX_RETRIES"
echo "stages=$STAGES"
echo "prebuild=disabled"

env \
  RUN_ID="$RUN_ID" \
  STAGES="$STAGES" \
  SOURCE_TASKS_ROOT="$SOURCE_TASKS_ROOT" \
  TASKS_GEN_ROOT="$TASKS_GEN_ROOT" \
  RUN_HARBOR="$RUN_HARBOR" \
  NO_DELETE="$NO_DELETE" \
  EXPERIMENT_JOBS_ROOT="$EXPERIMENT_JOBS_ROOT" \
  POLICY_JOB="$POLICY_JOB" \
  PERMISSION_TASK_SUFFIX="$PERMISSION_TASK_SUFFIX" \
  PERMISSION_GEN_MODEL_NAME="$PERMISSION_GEN_MODEL_NAME" \
  PERMISSION_GEN_REASONING_EFFORT="$PERMISSION_GEN_REASONING_EFFORT" \
  REPLAY_MODEL_NAME="$REPLAY_MODEL_NAME" \
  PREBUILD_PREPARED_TASKS=0 \
  PREBUILD_GENERATED_REPLAY_TASKS=0 \
  CLEAN_PREPARED_ROOTS="$CLEAN_PREPARED_ROOTS" \
  CLEAN_GENERATED_REPLAY="$CLEAN_GENERATED_REPLAY" \
  PERMISSION_GEN_N_ATTEMPTS="$PERMISSION_GEN_N_ATTEMPTS" \
  PERMISSION_GEN_N_CONCURRENT_TRIALS="$PERMISSION_GEN_N_CONCURRENT_TRIALS" \
  PERMISSION_GEN_MAX_TURNS="$PERMISSION_GEN_MAX_TURNS" \
  RETRY_MAX_RETRIES="$RETRY_MAX_RETRIES" \
  GENERATED_REPLAY_N_ATTEMPTS="$GENERATED_REPLAY_N_ATTEMPTS" \
  GENERATED_REPLAY_N_CONCURRENT_TRIALS="$GENERATED_REPLAY_N_CONCURRENT_TRIALS" \
  VERIFIER_TIMEOUT_SEC="$VERIFIER_TIMEOUT_SEC" \
  AGENT_TIMEOUT_SEC="$AGENT_TIMEOUT_SEC" \
  BUILD_TIMEOUT_SEC="$BUILD_TIMEOUT_SEC" \
  "$ROOT_DIR/experiments/full/run.sh"
