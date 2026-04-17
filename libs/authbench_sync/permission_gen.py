from __future__ import annotations

from pathlib import Path

from .common import (
    POLICY_OUTPUT_PATH,
    _as_path,
    copy_task,
    list_task_skill_dirs,
    replace_instruction,
    set_task_metadata_fields,
    slugify_name,
)
from .env_bases import ensure_local_prebuilt_compose_override, rewrite_task_dockerfile_to_shared_base
from .file_rwx import (
    append_default_task_skill_implicit_read,
    load_permission_eval_spec_file,
    write_permission_eval_spec_file,
)

DEFAULT_PERMISSION_GEN_PROMPT_PATH = (
    Path(__file__).resolve().parents[1] / "permission_gen_prompt" / "prompt_en.txt"
)
PERMISSION_GEN_VERIFIER_SCRIPT_PATH = (
    Path(__file__).resolve().parent / "assets" / "permission_gen_verifier.py"
)
PERMISSION_EVAL_SHARED_SCRIPT_PATH = Path(__file__).resolve().parent / "permission_eval_shared.py"

PERMISSION_GEN_TEST_SH = """#!/bin/bash

set -eu

python3 /tests/permission_metrics.py
"""

PERMISSION_GEN_SOLVE_SH = f"""#!/bin/bash

cat > {POLICY_OUTPUT_PATH} <<'EOF'
{{
  "read": [],
  "write": [],
  "execute": []
}}
EOF
"""

TASK_SKILL_PERMISSION_PROMPT = """
## Task Skill Context

This task ships task-local skills under `/app/skills`.
The executing agent can already read those skill files by default.
Do not add `/app/skills/**` to `authorization_policy.json` just because the task references a skill.
Focus the generated policy on the task's non-skill file permissions.
""".strip()


def sync_permission_gen_task(
    src: str | Path,
    dst: str | Path,
    prompt_template_path: str | Path | None = None,
) -> Path:
    task_path = copy_task(src, dst)
    source_task_name = Path(src).expanduser().resolve().name
    dockerfile_path = task_path / "environment" / "Dockerfile"
    has_task_skills = bool(list_task_skill_dirs(task_path))

    original_instruction = (task_path / "instruction.md").read_text(encoding="utf-8")
    rendered_instruction = _render_permission_prompt(
        prompt_template_path or DEFAULT_PERMISSION_GEN_PROMPT_PATH,
        original_instruction,
        has_task_skills=has_task_skills,
    )
    replace_instruction(task_path, rendered_instruction)

    (task_path / "tests" / "test.sh").write_text(PERMISSION_GEN_TEST_SH, encoding="utf-8")
    (task_path / "tests" / "permission_metrics.py").write_text(
        PERMISSION_GEN_VERIFIER_SCRIPT_PATH.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (task_path / "tests" / "permission_eval_shared.py").write_text(
        PERMISSION_EVAL_SHARED_SCRIPT_PATH.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    extra_pytest = task_path / "tests" / "test_state.py"
    if extra_pytest.exists():
        extra_pytest.unlink()
    if has_task_skills:
        _inject_default_task_skill_implicit_permissions(task_path)

    (task_path / "solution" / "solve.sh").write_text(PERMISSION_GEN_SOLVE_SH, encoding="utf-8")
    dockerfile_path.write_text(
        rewrite_task_dockerfile_to_shared_base(
            dockerfile_path.read_text(encoding="utf-8"),
            mode="plain",
        ),
        encoding="utf-8",
    )
    set_task_metadata_fields(
        task_path,
        {
            "authbench_source_task_name": source_task_name,
            "authbench_prebuilt_image_tag": f"authbench-{slugify_name(source_task_name)}-permission-gen:local",
        },
    )
    ensure_local_prebuilt_compose_override(task_path)
    return task_path


def _render_permission_prompt(
    prompt_template_path: str | Path,
    task_instruction: str,
    *,
    has_task_skills: bool,
) -> str:
    template_path = _as_path(prompt_template_path)
    template = template_path.read_text(encoding="utf-8")
    if "{task_instruction}" not in template:
        raise ValueError(f"Prompt template must contain {{task_instruction}}: {template_path}")
    rendered = template.replace("{task_instruction}", task_instruction.strip())
    if not has_task_skills:
        return rendered
    return f"{rendered.rstrip()}\n\n{TASK_SKILL_PERMISSION_PROMPT}\n"


def _inject_default_task_skill_implicit_permissions(task_path: Path) -> None:
    spec_path = task_path / "tests" / "permission_eval_spec.json"
    spec = append_default_task_skill_implicit_read(
        load_permission_eval_spec_file(spec_path),
    )
    write_permission_eval_spec_file(spec_path, spec)
