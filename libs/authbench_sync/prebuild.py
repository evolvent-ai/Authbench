from __future__ import annotations

import subprocess
from pathlib import Path

from .common import (
    load_task_metadata,
    set_task_environment_fields,
    slugify_name,
    validate_task_dir,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_TASK_IMAGE_SCRIPT = REPO_ROOT / "docker" / "scripts" / "build-task-image.sh"


def default_task_image_tag(task_dir: str | Path) -> str:
    task_path = validate_task_dir(task_dir)
    metadata = load_task_metadata(task_path)
    override = metadata.get("authbench_prebuilt_image_tag")
    if isinstance(override, str) and override.strip():
        return override.strip()
    slug = slugify_name(task_path.name)
    return f"authbench-{slug}:local"


def set_task_docker_image(task_dir: str | Path, docker_image: str) -> Path:
    return set_task_environment_fields(task_dir, {"docker_image": docker_image})


def prebuild_task_image(task_dir: str | Path, *, image_tag: str | None = None) -> tuple[str, Path]:
    task_path = validate_task_dir(task_dir)
    resolved_tag = image_tag or default_task_image_tag(task_path)

    subprocess.run(
        [str(BUILD_TASK_IMAGE_SCRIPT), resolved_tag, str(task_path)],
        check=True,
        cwd=REPO_ROOT,
    )
    task_toml_path = set_task_docker_image(task_path, resolved_tag)
    return resolved_tag, task_toml_path
