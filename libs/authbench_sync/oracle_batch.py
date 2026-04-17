from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .openclaw_replay import AUTHBENCH_ROOT
from .plan_registry import (
    build_planned_tasks,
    build_standard_manifest_payload,
    write_dataset_job_yaml,
    write_json_payload,
    write_local_registry,
)
from .replay_batch import list_task_dirs

DEFAULT_ORACLE_PLAN_ROOT = AUTHBENCH_ROOT / "plans" / "oracle"
DEFAULT_ORACLE_JOBS_DIR = AUTHBENCH_ROOT / "jobs"
ORACLE_DESCRIPTION_PREFIX = "Oracle validation tasks"


@dataclass(frozen=True, slots=True)
class OraclePlan:
    plan_dir: Path
    manifest_path: Path
    registry_path: Path
    job_yaml_path: Path
    task_paths: tuple[Path, ...]
    dataset_names: tuple[str, ...]


def materialize_oracle_plan(
    tasks_root: str | Path,
    *,
    plan_dir: str | Path,
    job_name: str,
    n_attempts: int = 1,
    n_concurrent_trials: int = 1,
    jobs_dir: str | Path = DEFAULT_ORACLE_JOBS_DIR,
) -> OraclePlan:
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
        description_prefix=ORACLE_DESCRIPTION_PREFIX,
    )
    job_yaml_path = write_dataset_job_yaml(
        registry_path=registry_path,
        dataset_names=dataset_names,
        output_path=resolved_plan_dir / "job.yaml",
        job_name=job_name,
        n_attempts=n_attempts,
        n_concurrent_trials=n_concurrent_trials,
        jobs_dir=jobs_dir,
        agent_block=_render_oracle_agent_block(),
    )
    manifest_payload["datasets"] = list(dataset_names)
    manifest_payload["registry_path"] = str(registry_path)
    manifest_payload["job_yaml_path"] = str(job_yaml_path)
    write_json_payload(manifest_path, manifest_payload)
    return OraclePlan(
        plan_dir=resolved_plan_dir,
        manifest_path=manifest_path,
        registry_path=registry_path,
        job_yaml_path=job_yaml_path,
        task_paths=tuple(task.task_path for task in planned_tasks),
        dataset_names=dataset_names,
    )


def _render_oracle_agent_block() -> str:
    return "  - name: oracle\n"
