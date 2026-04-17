from __future__ import annotations

import re
import shutil
import tomllib
from dataclasses import dataclass
from pathlib import Path

import toml

REQUIRED_TASK_PATHS = (
    "instruction.md",
    "task.toml",
    "environment",
    "solution",
    "tests",
)
ENVIRONMENT_DIR_NAME = "environment"
TASK_SKILLS_DIR_NAME = "skills"
TASK_SKILL_MARKDOWN_NAME = "SKILL.md"
DEFAULT_TASK_SKILLS_IMPLICIT_READ_PATTERN = "/app/skills/**"
POLICY_OUTPUT_PATH = "/app/authorization_policy.json"
DEFAULT_EVAL_DATASET = "standard"
SENSITIVE_EVAL_DATASET = "sensitive"
DEFAULT_SENSITIVE_MODE = "mixed"
SAFETY_ONLY_SENSITIVE_MODE = "safety_only"
EVAL_DATASET_METADATA_KEY = "authbench_eval_dataset"
SENSITIVE_MODE_METADATA_KEY = "authbench_sensitive_mode"
VALID_EVAL_DATASETS = frozenset({DEFAULT_EVAL_DATASET, SENSITIVE_EVAL_DATASET})
VALID_SENSITIVE_MODES = frozenset(
    {DEFAULT_SENSITIVE_MODE, SAFETY_ONLY_SENSITIVE_MODE}
)


@dataclass(frozen=True, slots=True)
class TaskEvalConfig:
    dataset: str
    sensitive_mode: str | None = None

    @property
    def is_sensitive(self) -> bool:
        return self.dataset == SENSITIVE_EVAL_DATASET

    @property
    def is_safety_only(self) -> bool:
        return self.sensitive_mode == SAFETY_ONLY_SENSITIVE_MODE


def _as_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def validate_task_dir(task_dir: str | Path) -> Path:
    path = _as_path(task_dir)
    if not path.is_dir():
        raise ValueError(f"Task directory does not exist: {path}")

    missing = [name for name in REQUIRED_TASK_PATHS if not (path / name).exists()]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Task directory is incomplete: {path} (missing: {joined})")

    _validate_task_skills(path)
    return path


def list_task_skill_dirs(task_dir: str | Path) -> tuple[Path, ...]:
    task_path = validate_task_dir(task_dir)
    skills_dir = _task_skills_dir(task_path)
    if not skills_dir.is_dir():
        return ()
    return tuple(
        child.resolve()
        for child in sorted(skills_dir.iterdir())
        if child.is_dir() and not child.name.startswith(".")
    )


def copy_task(src: str | Path, dst: str | Path) -> Path:
    source = validate_task_dir(src)
    destination = _as_path(dst)

    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return destination


def rewrite_instruction(task_dir: str | Path, prefix: str | None = None) -> Path:
    task_path = validate_task_dir(task_dir)
    instruction_path = task_path / "instruction.md"

    if not prefix:
        return instruction_path

    original = instruction_path.read_text(encoding="utf-8")
    prefix_block = prefix.rstrip("\n")
    rewritten = f"{prefix_block}\n\n{original.lstrip()}"
    instruction_path.write_text(rewritten, encoding="utf-8")
    return instruction_path


def replace_instruction(task_dir: str | Path, content: str) -> Path:
    task_path = validate_task_dir(task_dir)
    instruction_path = task_path / "instruction.md"
    instruction_path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return instruction_path


def slugify_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_task_toml(task_dir: str | Path) -> dict[str, object]:
    task_path = validate_task_dir(task_dir)
    return _load_task_toml_payload(task_path)


def load_task_metadata(task_dir: str | Path) -> dict[str, object]:
    payload = load_task_toml(task_dir)
    metadata = payload.get("metadata")
    if metadata is None:
        return {}
    if not isinstance(metadata, dict):
        raise ValueError(f"Task metadata must be a TOML table: {validate_task_dir(task_dir)}")
    return metadata


def load_task_eval_config(task_dir: str | Path) -> TaskEvalConfig:
    task_path = validate_task_dir(task_dir)
    metadata = load_task_metadata(task_path)
    raw_dataset = metadata.get(EVAL_DATASET_METADATA_KEY, DEFAULT_EVAL_DATASET)
    if not isinstance(raw_dataset, str) or raw_dataset not in VALID_EVAL_DATASETS:
        valid = ", ".join(sorted(VALID_EVAL_DATASETS))
        raise ValueError(
            f"{task_path}: {EVAL_DATASET_METADATA_KEY} must be one of: {valid}"
        )

    raw_mode = metadata.get(SENSITIVE_MODE_METADATA_KEY)
    if raw_dataset == DEFAULT_EVAL_DATASET:
        if raw_mode is not None:
            raise ValueError(
                f"{task_path}: {SENSITIVE_MODE_METADATA_KEY} is only valid when "
                f"{EVAL_DATASET_METADATA_KEY} = \"{SENSITIVE_EVAL_DATASET}\""
            )
        return TaskEvalConfig(dataset=DEFAULT_EVAL_DATASET)

    if raw_mode is None:
        return TaskEvalConfig(
            dataset=SENSITIVE_EVAL_DATASET,
            sensitive_mode=DEFAULT_SENSITIVE_MODE,
        )
    if not isinstance(raw_mode, str) or raw_mode not in VALID_SENSITIVE_MODES:
        valid = ", ".join(sorted(VALID_SENSITIVE_MODES))
        raise ValueError(
            f"{task_path}: {SENSITIVE_MODE_METADATA_KEY} must be one of: {valid}"
        )
    return TaskEvalConfig(
        dataset=SENSITIVE_EVAL_DATASET,
        sensitive_mode=raw_mode,
    )


def set_task_metadata_fields(task_dir: str | Path, values: dict[str, object]) -> Path:
    task_path = validate_task_dir(task_dir)
    return _set_task_toml_table_fields(task_path, "metadata", values)


def set_task_environment_fields(task_dir: str | Path, values: dict[str, object]) -> Path:
    task_path = validate_task_dir(task_dir)
    return _set_task_toml_table_fields(task_path, "environment", values)


def _validate_task_skills(task_path: Path) -> None:
    legacy_root_skills_dir = task_path / TASK_SKILLS_DIR_NAME
    if legacy_root_skills_dir.exists():
        raise ValueError(
            "Task skills must live under "
            f"{task_path / ENVIRONMENT_DIR_NAME / TASK_SKILLS_DIR_NAME}, not {legacy_root_skills_dir}"
        )
    skills_dir = _task_skills_dir(task_path)
    if not skills_dir.exists():
        return
    if not skills_dir.is_dir():
        raise ValueError(f"Task skills path must be a directory: {skills_dir}")

    for child in sorted(skills_dir.iterdir()):
        if child.name.startswith("."):
            continue
        if not child.is_dir():
            raise ValueError(f"Task skills entries must be directories: {child}")
        skill_markdown_path = child / TASK_SKILL_MARKDOWN_NAME
        if not skill_markdown_path.is_file():
            raise ValueError(f"Task skill is missing {TASK_SKILL_MARKDOWN_NAME}: {child}")


def _task_skills_dir(task_path: Path) -> Path:
    return task_path / ENVIRONMENT_DIR_NAME / TASK_SKILLS_DIR_NAME


def _load_task_toml_payload(task_path: Path) -> dict[str, object]:
    return tomllib.loads((task_path / "task.toml").read_text(encoding="utf-8"))


def _write_task_toml_payload(task_path: Path, payload: dict[str, object]) -> Path:
    task_toml_path = task_path / "task.toml"
    task_toml_path.write_text(toml.dumps(payload), encoding="utf-8")
    return task_toml_path


def _set_task_toml_table_fields(task_path: Path, table_name: str, values: dict[str, object]) -> Path:
    payload = _load_task_toml_payload(task_path)
    table = payload.setdefault(table_name, {})
    if not isinstance(table, dict):
        raise ValueError(f"Task {table_name} must be a TOML table: {task_path}")
    table.update(values)
    return _write_task_toml_payload(task_path, payload)
