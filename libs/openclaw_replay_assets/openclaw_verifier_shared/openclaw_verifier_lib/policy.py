from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from libs.authbench_sync.file_rwx import (
    PermissionPolicy,
    normalize_permission_policy,
    permission_policy_to_payload,
)

_ALWAYS_ALLOWED_TOOLS = ("web_fetch", "web_search")

_AXIS_TO_TOOLS: dict[str, tuple[str, ...]] = {
    "read": ("read",),
    "write": ("edit", "write"),
    "execute": ("exec", "process"),
}


@dataclass(frozen=True, slots=True)
class LoadedPolicy:
    mapped_tools: list[str]
    permission_policy: PermissionPolicy
    normalized_policy: dict[str, object]


def load_policy(policy_path: Path) -> tuple[LoadedPolicy | None, dict[str, object]]:
    if not policy_path.exists():
        return None, {
            "policy_found": False,
            "error": "Missing required policy file /opt/authbench/authorization_policy.json",
        }

    raw = policy_path.read_text(encoding="utf-8")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, {
            "policy_found": True,
            "policy_valid_json": False,
            "error": f"JSON parse error: {exc}",
        }

    if not isinstance(payload, dict):
        return None, {
            "policy_found": True,
            "policy_valid_json": True,
            "policy_is_object": False,
            "error": "Policy JSON must be an object.",
        }

    try:
        permission_policy = normalize_permission_policy(payload)
    except ValueError as exc:
        return None, {
            "policy_found": True,
            "policy_valid_json": True,
            "policy_is_object": True,
            "error": str(exc),
        }

    mapped: set[str] = set()
    if permission_policy.read:
        mapped.update(_AXIS_TO_TOOLS["read"])
    if permission_policy.write:
        mapped.update(_AXIS_TO_TOOLS["write"])
    if permission_policy.execute:
        mapped.update(_AXIS_TO_TOOLS["execute"])

    mapped_tools = sorted(mapped.union(_ALWAYS_ALLOWED_TOOLS))
    normalized_policy = permission_policy_to_payload(permission_policy)
    loaded = LoadedPolicy(
        mapped_tools=mapped_tools,
        permission_policy=permission_policy,
        normalized_policy=normalized_policy,
    )

    return loaded, {
        "policy_found": True,
        "policy_valid_json": True,
        "policy_is_object": True,
        "mapped_tools": mapped_tools,
        "normalized_policy": normalized_policy,
    }
