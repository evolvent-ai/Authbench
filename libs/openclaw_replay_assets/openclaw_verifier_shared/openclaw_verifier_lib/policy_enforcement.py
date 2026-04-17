from __future__ import annotations

import glob
import json
import os
import posixpath
import shlex
import uuid
from pathlib import Path

from libs.authbench_sync.file_rwx import PermissionPolicy
from libs.authbench_sync.permission_eval_shared import (
    join_pattern,
    normalize_exact_path,
    pattern_has_segment_glob,
    split_subtree_pattern,
)

POLICY_GUARD_PLUGIN_ID = "authbench-policy-guard"
LANDLOCK_LAUNCHER_PATH = "/usr/local/bin/authbench-landlock-launch"


def derive_exec_allowlist_patterns(execute_permissions: list[str] | tuple[str, ...]) -> list[str]:
    if not execute_permissions:
        return []
    return ["*"]


def write_exec_approvals(
    *,
    home_dir: Path,
    agent_id: str,
    execute_permissions: list[str] | tuple[str, ...],
) -> dict[str, object]:
    allowlist_patterns = derive_exec_allowlist_patterns(execute_permissions)
    approvals_path = home_dir / ".openclaw" / "exec-approvals.json"
    approvals_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": 1,
        "defaults": {
            "security": "full",
            "ask": "off",
            "askFallback": "deny",
            "autoAllowSkills": False,
        },
        "agents": {
            agent_id: {
                "security": "full",
                "ask": "off",
                "askFallback": "deny",
                "autoAllowSkills": False,
                "allowlist": [
                    {
                        "id": str(uuid.uuid4()),
                        "pattern": pattern,
                    }
                    for pattern in allowlist_patterns
                ],
            }
        },
    }
    approvals_path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )

    return {
        "exec_allowlist_path": str(approvals_path),
        "exec_allowlist_patterns": allowlist_patterns,
        "exec_allowlist_count": len(allowlist_patterns),
    }


def build_landlock_command(
    *,
    permission_policy: PermissionPolicy,
    implicit_permissions: PermissionPolicy,
    command_argv: list[str],
) -> str:
    if not command_argv:
        raise ValueError("Landlock command requires a non-empty argv")

    read_patterns = _dedupe(
        _expand_runtime_patterns(permission_policy.read),
        _expand_runtime_patterns(permission_policy.execute),
        _expand_runtime_patterns(implicit_permissions.read),
        _expand_runtime_patterns(implicit_permissions.execute),
    )
    write_patterns = _dedupe(
        _expand_write_patterns(_expand_runtime_patterns(permission_policy.write)),
        _expand_write_patterns(_expand_runtime_patterns(implicit_permissions.write)),
    )
    execute_patterns = _dedupe(
        _expand_runtime_patterns(permission_policy.execute),
        _expand_runtime_patterns(implicit_permissions.execute),
    )

    parts = [shlex.quote(LANDLOCK_LAUNCHER_PATH)]
    for pattern in read_patterns:
        parts.extend(["--read", shlex.quote(pattern)])
    for pattern in write_patterns:
        parts.extend(["--write", shlex.quote(pattern)])
    for pattern in execute_patterns:
        parts.extend(["--execute", shlex.quote(pattern)])
    parts.append("--")
    parts.extend(shlex.quote(arg) for arg in command_argv)
    return " ".join(parts)


def _expand_write_patterns(patterns: tuple[str, ...]) -> tuple[str, ...]:
    expanded: list[str] = []
    for pattern in patterns:
        if pattern.endswith("/**"):
            expanded.append(pattern)
            continue
        parent = posixpath.dirname(pattern) or "/"
        expanded.append(parent + "/**" if parent != "/" else "/")
    return tuple(expanded)


def _expand_runtime_patterns(patterns: tuple[str, ...]) -> tuple[str, ...]:
    expanded: list[str] = []
    for pattern in patterns:
        if not pattern_has_segment_glob(pattern):
            expanded.append(pattern)
            continue

        base_pattern, recursive = split_subtree_pattern(pattern)
        for match in sorted(glob.glob(base_pattern)):
            normalized_match = normalize_exact_path(match, field="runtime permission pattern")
            if recursive:
                if os.path.isdir(normalized_match):
                    expanded.append(join_pattern(normalized_match, recursive=True))
                continue
            expanded.append(normalized_match)
    return tuple(expanded)


def _dedupe(*groups: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group:
            if item in seen:
                continue
            seen.add(item)
            ordered.append(item)
    return tuple(ordered)
