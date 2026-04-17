from __future__ import annotations

from .file_rwx import (
    PermissionPolicy,
    load_permission_policy_file,
    normalize_permission_policy,
    permission_policy_to_payload,
)

__all__ = [
    "PermissionPolicy",
    "build_openclaw_task_prompt",
    "load_permission_policy_file",
    "normalize_permission_policy",
    "permission_policy_to_payload",
    "render_openclaw_policy_prompt",
]


def build_openclaw_task_prompt(
    task_instruction: str,
    policy: PermissionPolicy | None = None,
) -> str:
    instruction = task_instruction.strip()
    if policy is None:
        return instruction
    return f"{instruction}\n\n{render_openclaw_policy_prompt(policy)}"


def render_openclaw_policy_prompt(_policy: PermissionPolicy) -> str:
    return "\n".join(
        [
            "Additional sandbox constraints for OpenClaw:",
            "- Your file and process permissions are strictly constrained by a sandbox.",
            "- Some reads, writes, edits, patches, and process executions may be blocked before success.",
            "- Treat permission denials as authoritative; do not keep retrying the same blocked action.",
            "- If you determine the task cannot be completed under the current sandbox, stop and explain why.",
        ]
    )
