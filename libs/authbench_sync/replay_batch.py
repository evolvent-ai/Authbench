from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .common import (
    EVAL_DATASET_METADATA_KEY,
    REQUIRED_TASK_PATHS,
    SENSITIVE_MODE_METADATA_KEY,
    load_task_eval_config,
    set_task_metadata_fields,
    validate_task_dir,
)
from .file_rwx import load_permission_policy_file
from .openclaw_replay import (
    AUTHBENCH_ROOT,
    DEFAULT_REPLAY_AGENT_TIMEOUT_SEC,
    DEFAULT_REPLAY_BUILD_TIMEOUT_SEC,
    DEFAULT_REPLAY_VERIFIER_TIMEOUT_SEC,
    resolve_permission_job_trials,
    sync_openclaw_replay_task,
)
from .plan_registry import (
    PlannedTask,
    build_planned_tasks,
    build_standard_manifest_payload,
    replay_metric_scripts,
    write_dataset_job_yaml,
    write_json_payload,
    write_local_registry,
)

DEFAULT_GENERATED_REPLAY_PLAN_ROOT = AUTHBENCH_ROOT / "plans" / "generated_replay"
DEFAULT_REPLAY_PLAN_ROOT = AUTHBENCH_ROOT / "plans" / "replay"
DEFAULT_GENERATED_REPLAY_JOBS_DIR = AUTHBENCH_ROOT / "jobs_replay"
REPLAY_DESCRIPTION_PREFIX = "Replay tasks"
GENERATED_REPLAY_DESCRIPTION_PREFIX = "Generated-policy replay tasks"


@dataclass(frozen=True, slots=True)
class ReplayPlan:
    plan_dir: Path
    manifest_path: Path
    registry_path: Path
    job_yaml_path: Path
    synced_task_paths: tuple[Path, ...]
    dataset_names: tuple[str, ...]


def list_task_dirs(tasks_root: str | Path) -> list[Path]:
    root = Path(tasks_root).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    try:
        validate_task_dir(root)
    except ValueError:
        pass
    else:
        return [root]
    task_dirs = [
        candidate.resolve()
        for candidate in sorted(root.iterdir())
        if candidate.is_dir() and all((candidate / name).exists() for name in REQUIRED_TASK_PATHS)
    ]
    if not task_dirs:
        raise ValueError(f"No Harbor task directories found under {root}")
    return task_dirs


def write_openclaw_replay_job_yaml(
    task_paths: list[str | Path],
    output_path: str | Path,
    *,
    job_name: str,
    model_name: str,
    n_attempts: int,
    n_concurrent_trials: int,
    jobs_dir: str = "jobs",
    retry_max_retries: int = 0,
) -> Path:
    if n_attempts <= 0:
        raise ValueError("n_attempts must be > 0")
    if n_concurrent_trials <= 0:
        raise ValueError("n_concurrent_trials must be > 0")
    if retry_max_retries < 0:
        raise ValueError("retry_max_retries must be >= 0")

    resolved_paths = [Path(task_path).expanduser().resolve() for task_path in task_paths]
    if not resolved_paths:
        raise ValueError("task_paths must not be empty")

    task_lines = "\n".join(
        f"  - path: {_render_task_path(task_path)}" for task_path in resolved_paths
    )
    metric_block = _render_replay_metric_block_if_homogeneous(resolved_paths)
    retry_block = ""
    if retry_max_retries > 0:
        retry_block = f"retry:\n  max_retries: {retry_max_retries}\n\n"
    yaml_text = (
        f"job_name: {job_name}\n"
        f"jobs_dir: {jobs_dir}\n"
        f"n_attempts: {n_attempts}\n"
        f"n_concurrent_trials: {n_concurrent_trials}\n\n"
        f"{retry_block}"
        "environment:\n"
        "  force_build: false\n"
        "  delete: false\n\n"
        f"{metric_block}"
        "tasks:\n"
        f"{task_lines}\n\n"
        "agents:\n"
        "  - import_path: libs.authbench_harbor_agents.openclaw_agent:OpenClawAgent\n"
        f"    model_name: {model_name}\n"
    )

    destination = Path(output_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(yaml_text, encoding="utf-8")
    return destination


def materialize_generated_replay_plan(
    src_root: str | Path,
    dst_root: str | Path,
    *,
    policy_job: str | Path,
    plan_dir: str | Path,
    job_name: str,
    model_name: str = "gpt-5",
    n_attempts: int = 1,
    n_concurrent_trials: int = 10,
    jobs_dir: str | Path = DEFAULT_GENERATED_REPLAY_JOBS_DIR,
    verifier_timeout_sec: float = DEFAULT_REPLAY_VERIFIER_TIMEOUT_SEC,
    agent_timeout_sec: float = DEFAULT_REPLAY_AGENT_TIMEOUT_SEC,
    build_timeout_sec: float = DEFAULT_REPLAY_BUILD_TIMEOUT_SEC,
    retry_max_retries: int = 0,
) -> ReplayPlan:
    source_root = Path(src_root).expanduser().resolve()
    if not source_root.is_dir():
        raise FileNotFoundError(source_root)

    destination_root = Path(dst_root).expanduser().resolve()
    destination_root.mkdir(parents=True, exist_ok=True)
    resolved_plan_dir = Path(plan_dir).expanduser().resolve()
    resolved_plan_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = resolved_plan_dir / "manifest.json"

    synced_task_paths: list[Path] = []
    planned_tasks: list[PlannedTask] = []
    manifest_entries: list[dict[str, object]] = []
    for trial in resolve_permission_job_trials(policy_job):
        source_task_path = source_root / trial.source_task_name
        entry: dict[str, object] = {
            "trial_name": trial.trial_name,
            "source_task_name": trial.source_task_name,
            "source_task_path": str(source_task_path),
            "permission_task_path": str(trial.permission_task_path),
            "policy_artifact_path": str(trial.policy_artifact_path),
        }
        if not source_task_path.is_dir():
            entry["status"] = "skipped_missing_source_task"
            entry["error"] = f"Source task not found: {source_task_path}"
            manifest_entries.append(entry)
            continue
        if not trial.policy_artifact_path.is_file():
            entry["status"] = "skipped_missing_policy"
            entry["error"] = f"Missing policy artifact: {trial.policy_artifact_path}"
            manifest_entries.append(entry)
            continue

        try:
            load_permission_policy_file(trial.policy_artifact_path)
        except Exception as exc:
            entry["status"] = "skipped_invalid_policy"
            entry["error"] = str(exc)
            manifest_entries.append(entry)
            continue

        eval_config = load_task_eval_config(source_task_path)
        task_name = f"{trial.source_task_name}-generated-{_trial_suffix(trial.trial_name)}"
        destination_task_path = destination_root / task_name
        replay_task_path = sync_openclaw_replay_task(
            source_task_path,
            destination_task_path,
            policy_path=trial.policy_artifact_path,
            verifier_timeout_sec=verifier_timeout_sec,
            agent_timeout_sec=agent_timeout_sec,
            build_timeout_sec=build_timeout_sec,
        )
        set_task_metadata_fields(
            replay_task_path,
            {
                "authbench_permission_gen_job_name": Path(policy_job).name,
                "authbench_permission_gen_trial_name": trial.trial_name,
                EVAL_DATASET_METADATA_KEY: eval_config.dataset,
                **(
                    {SENSITIVE_MODE_METADATA_KEY: eval_config.sensitive_mode}
                    if eval_config.is_sensitive
                    else {}
                ),
            },
        )
        planned_tasks.append(
            PlannedTask(
                task_name=task_name,
                task_path=replay_task_path.resolve(),
                eval_config=eval_config,
            )
        )
        synced_task_paths.append(replay_task_path.resolve())
        entry["status"] = "synced"
        entry["eval_dataset"] = eval_config.dataset
        entry["sensitive_mode"] = eval_config.sensitive_mode
        entry["replay_task_path"] = str(replay_task_path.resolve())
        manifest_entries.append(entry)

    manifest_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "policy_job": str(policy_job),
        "source_root": str(source_root),
        "destination_root": str(destination_root),
        "plan_dir": str(resolved_plan_dir),
        "synced_task_count": len(synced_task_paths),
        "datasets": sorted({task.eval_config.dataset for task in planned_tasks}),
        "entries": manifest_entries,
    }
    write_json_payload(manifest_path, manifest_payload)
    if not planned_tasks:
        raise ValueError(
            f"No valid generated-policy replay tasks were created; see {manifest_path}"
        )

    registry_path, dataset_names = write_local_registry(
        planned_tasks,
        resolved_plan_dir / "registry.json",
        dataset_metric_scripts=replay_metric_scripts(),
        description_prefix=GENERATED_REPLAY_DESCRIPTION_PREFIX,
    )
    job_yaml_path = write_dataset_job_yaml(
        registry_path=registry_path,
        dataset_names=dataset_names,
        output_path=resolved_plan_dir / "job.yaml",
        job_name=job_name,
        n_attempts=n_attempts,
        n_concurrent_trials=n_concurrent_trials,
        jobs_dir=jobs_dir,
        retry_max_retries=retry_max_retries,
        agent_block=_render_replay_agent_block(model_name),
    )
    manifest_payload["datasets"] = list(dataset_names)
    manifest_payload["registry_path"] = str(registry_path)
    manifest_payload["job_yaml_path"] = str(job_yaml_path)
    write_json_payload(manifest_path, manifest_payload)
    return ReplayPlan(
        plan_dir=resolved_plan_dir,
        manifest_path=manifest_path,
        registry_path=registry_path,
        job_yaml_path=job_yaml_path,
        synced_task_paths=tuple(synced_task_paths),
        dataset_names=dataset_names,
    )


def materialize_replay_plan(
    tasks_root: str | Path,
    *,
    plan_dir: str | Path,
    job_name: str,
    model_name: str = "gpt-5",
    n_attempts: int = 1,
    n_concurrent_trials: int = 1,
    jobs_dir: str | Path = DEFAULT_GENERATED_REPLAY_JOBS_DIR,
    retry_max_retries: int = 0,
) -> ReplayPlan:
    resolved_task_paths = list_task_dirs(tasks_root)
    resolved_plan_dir = Path(plan_dir).expanduser().resolve()
    resolved_plan_dir.mkdir(parents=True, exist_ok=True)
    planned_tasks = build_planned_tasks(resolved_task_paths)
    manifest_path = resolved_plan_dir / "manifest.json"
    manifest_payload = build_standard_manifest_payload(
        tasks_root=tasks_root,
        plan_dir=resolved_plan_dir,
        planned_tasks=planned_tasks,
    )
    write_json_payload(manifest_path, manifest_payload)
    registry_path, dataset_names = write_local_registry(
        planned_tasks,
        resolved_plan_dir / "registry.json",
        dataset_metric_scripts=replay_metric_scripts(),
        description_prefix=REPLAY_DESCRIPTION_PREFIX,
    )
    job_yaml_path = write_dataset_job_yaml(
        registry_path=registry_path,
        dataset_names=dataset_names,
        output_path=resolved_plan_dir / "job.yaml",
        job_name=job_name,
        n_attempts=n_attempts,
        n_concurrent_trials=n_concurrent_trials,
        jobs_dir=jobs_dir,
        retry_max_retries=retry_max_retries,
        agent_block=_render_replay_agent_block(model_name),
    )
    manifest_payload["datasets"] = list(dataset_names)
    manifest_payload["registry_path"] = str(registry_path)
    manifest_payload["job_yaml_path"] = str(job_yaml_path)
    write_json_payload(manifest_path, manifest_payload)
    return ReplayPlan(
        plan_dir=resolved_plan_dir,
        manifest_path=manifest_path,
        registry_path=registry_path,
        job_yaml_path=job_yaml_path,
        synced_task_paths=tuple(task.task_path for task in planned_tasks),
        dataset_names=dataset_names,
    )


def _render_task_path(task_path: Path) -> str:
    try:
        return task_path.relative_to(AUTHBENCH_ROOT).as_posix()
    except ValueError:
        return str(task_path)


def _render_replay_metric_block_if_homogeneous(task_paths: list[Path]) -> str:
    dataset_names = {load_task_eval_config(task_path).dataset for task_path in task_paths}
    if len(dataset_names) != 1:
        return ""
    dataset_name = next(iter(dataset_names))
    metric_script = replay_metric_scripts().get(dataset_name)
    if metric_script is None:
        raise ValueError(f"Missing replay metric script for dataset: {dataset_name}")
    return (
        "metrics:\n"
        "  - type: uv-script\n"
        "    kwargs:\n"
        f"      script_path: {metric_script.resolve()}\n\n"
    )


def _trial_suffix(trial_name: str) -> str:
    if "__" in trial_name:
        return trial_name.split("__", 1)[1]
    return trial_name


def _render_replay_agent_block(model_name: str) -> str:
    return (
        "  - import_path: libs.authbench_harbor_agents.openclaw_agent:OpenClawAgent\n"
        f"    model_name: {model_name}\n"
    )
