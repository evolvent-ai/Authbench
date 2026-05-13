from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .common import validate_task_dir
from .file_rwx import load_permission_policy_file
from .openclaw_replay import AUTHBENCH_ROOT, resolve_permission_job_trials
from .permission_batch import (
    AUTH_TIGHTNESS_AGENT_PROFILE,
    DEFAULT_PERMISSION_GEN_JOBS_DIR,
    DEFAULT_PERMISSION_GEN_MAX_TURNS,
    PermissionGenPlan,
    materialize_permission_gen_plan,
)
from .permission_gen import sync_tightness_permission_gen_task
from .plan_registry import write_json_payload

DEFAULT_ST_TIGHTNESS_PLAN_ROOT = AUTHBENCH_ROOT / "plans" / "st_tightness"


@dataclass(frozen=True, slots=True)
class STTightnessPlan:
    plan_dir: Path
    manifest_path: Path
    registry_path: Path
    job_yaml_path: Path
    synced_task_paths: tuple[Path, ...]
    dataset_names: tuple[str, ...]


def materialize_st_tightness_plan(
    src_root: str | Path,
    dst_root: str | Path,
    *,
    sufficiency_policy_job: str | Path,
    plan_dir: str | Path,
    job_name: str,
    model_name: str = "gpt-5",
    reasoning_effort: str | None = None,
    n_attempts: int = 1,
    n_concurrent_trials: int = 1,
    jobs_dir: str | Path = DEFAULT_PERMISSION_GEN_JOBS_DIR,
    max_turns: int = DEFAULT_PERMISSION_GEN_MAX_TURNS,
    retry_max_retries: int = 0,
) -> STTightnessPlan:
    source_root = Path(src_root).expanduser().resolve()
    if not source_root.is_dir():
        raise FileNotFoundError(source_root)

    destination_root = Path(dst_root).expanduser().resolve()
    destination_root.mkdir(parents=True, exist_ok=True)
    resolved_plan_dir = Path(plan_dir).expanduser().resolve()
    resolved_plan_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = resolved_plan_dir / "manifest.json"

    synced_task_paths: list[Path] = []
    manifest_entries: list[dict[str, object]] = []
    for trial in resolve_permission_job_trials(sufficiency_policy_job):
        source_task_path = _resolve_source_task_path(source_root, trial.source_task_name)
        task_name = f"{trial.source_task_name}-st-tight-{_trial_suffix(trial.trial_name)}"
        destination_task_path = destination_root / task_name
        entry: dict[str, object] = {
            "trial_name": trial.trial_name,
            "source_task_name": trial.source_task_name,
            "source_task_path": str(source_task_path),
            "sufficiency_policy_artifact_path": str(trial.policy_artifact_path),
            "tightness_task_path": str(destination_task_path),
        }

        if not source_task_path.is_dir():
            entry["status"] = "skipped_missing_source_task"
            entry["error"] = f"Source task not found: {source_task_path}"
            manifest_entries.append(entry)
            continue
        if not trial.policy_artifact_path.is_file():
            entry["status"] = "skipped_missing_sufficiency_policy"
            entry["error"] = f"Missing sufficiency policy artifact: {trial.policy_artifact_path}"
            manifest_entries.append(entry)
            continue

        try:
            load_permission_policy_file(trial.policy_artifact_path)
        except Exception as exc:
            entry["status"] = "skipped_invalid_sufficiency_policy"
            entry["error"] = str(exc)
            manifest_entries.append(entry)
            continue

        tightness_task_path = sync_tightness_permission_gen_task(
            source_task_path,
            destination_task_path,
            sufficiency_policy_path=trial.policy_artifact_path,
        )
        synced_task_paths.append(tightness_task_path.resolve())
        entry["status"] = "synced"
        entry["tightness_task_path"] = str(tightness_task_path.resolve())
        manifest_entries.append(entry)

    pre_plan_manifest_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "sufficiency_policy_job": str(sufficiency_policy_job),
        "source_root": str(source_root),
        "destination_root": str(destination_root),
        "plan_dir": str(resolved_plan_dir),
        "synced_task_count": len(synced_task_paths),
        "entries": manifest_entries,
    }
    write_json_payload(manifest_path, pre_plan_manifest_payload)
    if not synced_task_paths:
        raise ValueError(f"No valid tightness tasks were created; see {manifest_path}")

    permission_plan = materialize_permission_gen_plan(
        destination_root,
        plan_dir=resolved_plan_dir,
        job_name=job_name,
        model_name=model_name,
        reasoning_effort=reasoning_effort,
        n_attempts=n_attempts,
        n_concurrent_trials=n_concurrent_trials,
        jobs_dir=jobs_dir,
        max_turns=max_turns,
        retry_max_retries=retry_max_retries,
        agent_profile=AUTH_TIGHTNESS_AGENT_PROFILE,
    )
    _augment_permission_plan_manifest(
        permission_plan=permission_plan,
        sufficiency_policy_job=sufficiency_policy_job,
        source_root=source_root,
        destination_root=destination_root,
        manifest_entries=manifest_entries,
    )
    return STTightnessPlan(
        plan_dir=permission_plan.plan_dir,
        manifest_path=permission_plan.manifest_path,
        registry_path=permission_plan.registry_path,
        job_yaml_path=permission_plan.job_yaml_path,
        synced_task_paths=tuple(synced_task_paths),
        dataset_names=permission_plan.dataset_names,
    )


def _augment_permission_plan_manifest(
    *,
    permission_plan: PermissionGenPlan,
    sufficiency_policy_job: str | Path,
    source_root: Path,
    destination_root: Path,
    manifest_entries: list[dict[str, object]],
) -> None:
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "sufficiency_policy_job": str(sufficiency_policy_job),
        "source_root": str(source_root),
        "destination_root": str(destination_root),
        "plan_dir": str(permission_plan.plan_dir),
        "task_count": len(permission_plan.task_paths),
        "datasets": list(permission_plan.dataset_names),
        "registry_path": str(permission_plan.registry_path),
        "job_yaml_path": str(permission_plan.job_yaml_path),
        "entries": manifest_entries,
    }
    write_json_payload(permission_plan.manifest_path, payload)


def _resolve_source_task_path(source_root: Path, source_task_name: str) -> Path:
    try:
        validate_task_dir(source_root)
    except ValueError:
        return source_root / source_task_name
    if source_root.name == source_task_name:
        return source_root
    return source_root / source_task_name


def _trial_suffix(trial_name: str) -> str:
    if "__" in trial_name:
        return trial_name.split("__", 1)[1]
    return trial_name
