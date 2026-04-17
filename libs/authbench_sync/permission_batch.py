from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .openclaw_replay import AUTHBENCH_ROOT
from .plan_registry import (
    build_planned_tasks,
    build_standard_manifest_payload,
    permission_gen_metric_scripts,
    write_dataset_job_yaml,
    write_json_payload,
    write_local_registry,
)
from .replay_batch import list_task_dirs

DEFAULT_PERMISSION_GEN_PLAN_ROOT = AUTHBENCH_ROOT / "plans" / "permission_gen"
DEFAULT_PERMISSION_GEN_JOBS_DIR = AUTHBENCH_ROOT / "jobs-gen"
DEFAULT_PERMISSION_GEN_MAX_TURNS = 50
PERMISSION_GEN_DESCRIPTION_PREFIX = "Permission-generation tasks"
PERMISSION_GEN_POLICY_ARTIFACT = "/app/authorization_policy.json"


@dataclass(frozen=True, slots=True)
class PermissionGenPlan:
    plan_dir: Path
    manifest_path: Path
    registry_path: Path
    job_yaml_path: Path
    task_paths: tuple[Path, ...]
    dataset_names: tuple[str, ...]


def materialize_permission_gen_plan(
    tasks_root: str | Path,
    *,
    plan_dir: str | Path,
    job_name: str,
    model_name: str = "gpt-5",
    reasoning_effort: str | None = None,
    n_attempts: int = 1,
    n_concurrent_trials: int = 1,
    jobs_dir: str | Path = DEFAULT_PERMISSION_GEN_JOBS_DIR,
    max_turns: int = DEFAULT_PERMISSION_GEN_MAX_TURNS,
    retry_max_retries: int = 0,
) -> PermissionGenPlan:
    if max_turns <= 0:
        raise ValueError("max_turns must be > 0")

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
        dataset_metric_scripts=permission_gen_metric_scripts(),
        description_prefix=PERMISSION_GEN_DESCRIPTION_PREFIX,
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
        agent_block=_render_permission_gen_agent_block(
            model_name=model_name,
            reasoning_effort=reasoning_effort,
            max_turns=max_turns,
        ),
        artifacts=(PERMISSION_GEN_POLICY_ARTIFACT,),
    )
    manifest_payload["datasets"] = list(dataset_names)
    manifest_payload["registry_path"] = str(registry_path)
    manifest_payload["job_yaml_path"] = str(job_yaml_path)
    write_json_payload(manifest_path, manifest_payload)
    return PermissionGenPlan(
        plan_dir=resolved_plan_dir,
        manifest_path=manifest_path,
        registry_path=registry_path,
        job_yaml_path=job_yaml_path,
        task_paths=tuple(task.task_path for task in planned_tasks),
        dataset_names=dataset_names,
    )


def _render_permission_gen_agent_block(
    *,
    model_name: str,
    reasoning_effort: str | None,
    max_turns: int,
) -> str:
    reasoning_effort_block = ""
    if reasoning_effort:
        reasoning_effort_block = f"      reasoning_effort: {reasoning_effort}\n"
    return (
        "  - name: terminus-2\n"
        f"    model_name: {model_name}\n"
        "    kwargs:\n"
        f"{reasoning_effort_block}"
        f"      max_turns: {max_turns}\n"
    )
