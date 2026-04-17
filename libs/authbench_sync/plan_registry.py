from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .common import SENSITIVE_EVAL_DATASET, TaskEvalConfig, load_task_eval_config

STANDARD_DATASET = "standard"
STANDARD_REPLAY_METRIC_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "libs"
    / "authbench_metrics"
    / "replay_standard_uv_metric.py"
)
SENSITIVE_REPLAY_METRIC_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "libs"
    / "authbench_metrics"
    / "replay_sensitive_uv_metric.py"
)
PERMISSION_GEN_METRIC_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "libs"
    / "authbench_metrics"
    / "permission_gen_uv_metric.py"
)


@dataclass(frozen=True, slots=True)
class PlannedTask:
    task_name: str
    task_path: Path
    eval_config: TaskEvalConfig


def build_planned_tasks(task_paths: list[Path]) -> list[PlannedTask]:
    return [
        PlannedTask(
            task_name=task_path.name,
            task_path=task_path,
            eval_config=load_task_eval_config(task_path),
        )
        for task_path in task_paths
    ]


def build_standard_manifest_payload(
    *,
    tasks_root: str | Path,
    plan_dir: str | Path,
    planned_tasks: list[PlannedTask],
) -> dict[str, object]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "tasks_root": str(Path(tasks_root).expanduser().resolve()),
        "plan_dir": str(Path(plan_dir).expanduser().resolve()),
        "task_count": len(planned_tasks),
        "datasets": sorted({task.eval_config.dataset for task in planned_tasks}),
        "entries": [
            {
                "task_name": task.task_name,
                "task_path": str(task.task_path),
                "eval_dataset": task.eval_config.dataset,
                "sensitive_mode": task.eval_config.sensitive_mode,
                "status": "included",
            }
            for task in planned_tasks
        ],
    }


def write_json_payload(output_path: str | Path, payload: object) -> Path:
    destination = Path(output_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return destination


def write_local_registry(
    tasks: list[PlannedTask],
    output_path: str | Path,
    *,
    dataset_metric_scripts: dict[str, Path] | None = None,
    description_prefix: str,
) -> tuple[Path, tuple[str, ...]]:
    datasets: list[dict[str, object]] = []
    dataset_names: list[str] = []
    grouped = _group_tasks(tasks)
    for dataset_name in (STANDARD_DATASET, SENSITIVE_EVAL_DATASET):
        dataset_tasks = grouped.get(dataset_name, [])
        if not dataset_tasks:
            continue
        dataset_names.append(dataset_name)
        dataset_payload: dict[str, object] = {
            "name": dataset_name,
            "version": "v1",
            "description": f"{description_prefix} for {dataset_name} tasks",
            "tasks": [
                {
                    "name": task.task_name,
                    "path": str(task.task_path),
                }
                for task in dataset_tasks
            ],
        }
        if dataset_metric_scripts is not None:
            metric_script = dataset_metric_scripts.get(dataset_name)
            if metric_script is None:
                raise ValueError(f"Missing metric script for dataset: {dataset_name}")
            dataset_payload["metrics"] = [
                {
                    "type": "uv-script",
                    "kwargs": {
                        "script_path": str(metric_script)
                    },
                }
            ]
        datasets.append(dataset_payload)

    destination = Path(output_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(datasets, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return destination, tuple(dataset_names)


def write_dataset_job_yaml(
    *,
    registry_path: str | Path,
    dataset_names: tuple[str, ...],
    output_path: str | Path,
    job_name: str,
    n_attempts: int,
    n_concurrent_trials: int,
    jobs_dir: str | Path,
    agent_block: str,
    retry_max_retries: int = 0,
    artifacts: tuple[str, ...] = (),
) -> Path:
    if not dataset_names:
        raise ValueError("dataset_names must not be empty")
    if n_attempts <= 0:
        raise ValueError("n_attempts must be > 0")
    if n_concurrent_trials <= 0:
        raise ValueError("n_concurrent_trials must be > 0")
    if retry_max_retries < 0:
        raise ValueError("retry_max_retries must be >= 0")

    resolved_registry_path = Path(registry_path).expanduser().resolve()
    resolved_jobs_dir = Path(jobs_dir).expanduser().resolve()
    dataset_lines = "\n".join(
        (
            "  - registry:\n"
            f"      path: {resolved_registry_path}\n"
            f"    name: {dataset_name}\n"
            "    version: v1"
        )
        for dataset_name in dataset_names
    )
    artifacts_block = ""
    if artifacts:
        artifact_lines = "\n".join(f"  - {artifact}" for artifact in artifacts)
        artifacts_block = f"\nartifacts:\n{artifact_lines}\n"
    retry_block = ""
    if retry_max_retries > 0:
        retry_block = f"retry:\n  max_retries: {retry_max_retries}\n\n"
    yaml_text = (
        f"job_name: {job_name}\n"
        f"jobs_dir: {resolved_jobs_dir}\n"
        f"n_attempts: {n_attempts}\n"
        f"n_concurrent_trials: {n_concurrent_trials}\n\n"
        f"{retry_block}"
        "environment:\n"
        "  force_build: false\n"
        "  delete: false\n\n"
        "datasets:\n"
        f"{dataset_lines}\n\n"
        "agents:\n"
        f"{agent_block.rstrip()}\n"
        f"{artifacts_block}"
    )

    destination = Path(output_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(yaml_text, encoding="utf-8")
    return destination


def replay_metric_scripts() -> dict[str, Path]:
    return {
        STANDARD_DATASET: STANDARD_REPLAY_METRIC_SCRIPT,
        SENSITIVE_EVAL_DATASET: SENSITIVE_REPLAY_METRIC_SCRIPT,
    }


def permission_gen_metric_scripts() -> dict[str, Path]:
    return {
        STANDARD_DATASET: PERMISSION_GEN_METRIC_SCRIPT,
        SENSITIVE_EVAL_DATASET: PERMISSION_GEN_METRIC_SCRIPT,
    }


def _group_tasks(tasks: list[PlannedTask]) -> dict[str, list[PlannedTask]]:
    grouped: dict[str, list[PlannedTask]] = {}
    for task in tasks:
        grouped.setdefault(task.eval_config.dataset, []).append(task)
    return grouped
