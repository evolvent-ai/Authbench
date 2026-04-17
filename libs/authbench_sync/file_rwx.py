from __future__ import annotations

import json
from pathlib import Path

from .common import DEFAULT_TASK_SKILLS_IMPLICIT_READ_PATTERN, _as_path
from .permission_eval_shared import (
    PermissionEvalSpec,
    PermissionPolicy,
    append_implicit_permissions,
    normalize_permission_eval_spec,
    permission_eval_spec_to_payload,
    require_object,
)
from .permission_eval_shared import (
    normalize_permission_policy as _normalize_permission_policy,
)
from .permission_eval_shared import (
    permission_policy_to_payload as _permission_policy_to_payload,
)


def load_permission_policy_file(policy_path: str | Path) -> PermissionPolicy:
    payload = _load_json_object(_as_path(policy_path))
    return normalize_permission_policy(payload)


def normalize_permission_policy(payload: object) -> PermissionPolicy:
    return _normalize_permission_policy(payload)


def permission_policy_to_payload(policy: PermissionPolicy) -> dict[str, object]:
    return _permission_policy_to_payload(policy)


def load_permission_eval_spec_file(spec_path: str | Path) -> PermissionEvalSpec:
    payload = _load_json_object(_as_path(spec_path))
    return normalize_permission_eval_spec(payload)


def write_permission_eval_spec_file(spec_path: str | Path, spec: PermissionEvalSpec) -> Path:
    resolved_path = _as_path(spec_path)
    resolved_path.write_text(
        json.dumps(permission_eval_spec_to_payload(spec), ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return resolved_path


def append_default_task_skill_implicit_read(spec: PermissionEvalSpec) -> PermissionEvalSpec:
    return append_implicit_permissions(
        spec,
        read=(DEFAULT_TASK_SKILLS_IMPLICIT_READ_PATTERN,),
    )


def _load_json_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return require_object(payload, context=str(path))
