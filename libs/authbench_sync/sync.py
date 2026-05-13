from __future__ import annotations

from pathlib import Path

from .common import POLICY_OUTPUT_PATH, copy_task, rewrite_instruction
from .openclaw_prompt import (
    build_openclaw_task_prompt,
    load_permission_policy_file,
    normalize_permission_policy,
    permission_policy_to_payload,
    render_openclaw_policy_prompt,
)
from .openclaw_replay import sync_openclaw_replay_task
from .permission_gen import (
    DEFAULT_PERMISSION_GEN_PROMPT_PATH,
    DEFAULT_ST_SUFFICIENCY_PROMPT_PATH,
    DEFAULT_ST_TIGHTNESS_PROMPT_PATH,
    sync_permission_gen_task,
    sync_sufficiency_permission_gen_task,
    sync_tightness_permission_gen_task,
)

__all__ = [
    "DEFAULT_PERMISSION_GEN_PROMPT_PATH",
    "DEFAULT_ST_SUFFICIENCY_PROMPT_PATH",
    "DEFAULT_ST_TIGHTNESS_PROMPT_PATH",
    "POLICY_OUTPUT_PATH",
    "build_openclaw_task_prompt",
    "copy_task",
    "load_permission_policy_file",
    "normalize_permission_policy",
    "permission_policy_to_payload",
    "render_openclaw_policy_prompt",
    "rewrite_instruction",
    "sync_openclaw_replay_task",
    "sync_permission_gen_task",
    "sync_sufficiency_permission_gen_task",
    "sync_task",
    "sync_tightness_permission_gen_task",
]


def sync_task(src: str | Path, dst: str | Path, instruction_prefix: str | None = None) -> Path:
    task_path = copy_task(src, dst)
    rewrite_instruction(task_path, prefix=instruction_prefix)
    return task_path
