from __future__ import annotations

import fnmatch
import glob
import posixpath
from dataclasses import dataclass

_AXES = ("read", "write", "execute")
_EVAL_SPEC_KEYS = ("required_permissions", "scored_roots", "implicit_permissions")
_EVAL_SPEC_OPTIONAL_KEYS = ("sensitive_permissions",)


@dataclass(frozen=True, slots=True)
class PermissionPolicy:
    read: tuple[str, ...]
    write: tuple[str, ...]
    execute: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ScoredRoots:
    read: tuple[str, ...]
    write: tuple[str, ...]
    execute: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PermissionEvalSpec:
    required_permissions: PermissionPolicy
    scored_roots: ScoredRoots
    implicit_permissions: PermissionPolicy
    sensitive_permissions: PermissionPolicy | None = None


def require_object(payload: object, *, context: str) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be a JSON object")
    return payload


def require_exact_keys(
    payload: dict[str, object],
    *,
    expected: tuple[str, ...],
    context: str,
) -> None:
    actual = tuple(payload.keys())
    unexpected = [key for key in actual if key not in expected]
    missing = [key for key in expected if key not in payload]
    if missing:
        raise ValueError(f"{context} is missing required keys: {', '.join(missing)}")
    if unexpected:
        raise ValueError(f"{context} has unsupported keys: {', '.join(unexpected)}")


def require_allowed_keys(
    payload: dict[str, object],
    *,
    required: tuple[str, ...],
    optional: tuple[str, ...],
    context: str,
) -> None:
    actual = tuple(payload.keys())
    allowed = required + optional
    unexpected = [key for key in actual if key not in allowed]
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"{context} is missing required keys: {', '.join(missing)}")
    if unexpected:
        raise ValueError(f"{context} has unsupported keys: {', '.join(unexpected)}")


def require_string_list(raw: object, *, field: str) -> list[str]:
    if not isinstance(raw, list):
        raise ValueError(f"{field} must be a JSON array")

    values: list[str] = []
    for index, item in enumerate(raw):
        if not isinstance(item, str):
            raise ValueError(f"{field}[{index}] must be a string")
        stripped = item.strip()
        if not stripped:
            raise ValueError(f"{field}[{index}] must not be empty")
        values.append(stripped)
    return values


def normalize_absolute_path(value: str, *, field: str) -> str:
    raw = value.replace("\\", "/").strip()
    if not raw.startswith("/"):
        raise ValueError(f"{field} must use absolute POSIX paths: {value}")
    normalized = posixpath.normpath(raw)
    if not normalized.startswith("/"):
        raise ValueError(f"{field} must use absolute POSIX paths: {value}")
    return normalized


def split_subtree_pattern(pattern: str) -> tuple[str, bool]:
    normalized = pattern.replace("\\", "/").strip()
    if normalized == "/**":
        return "/", True
    if normalized.endswith("/**"):
        return normalized[:-3], True
    return normalized, False


def join_pattern(base: str, *, recursive: bool) -> str:
    if not recursive:
        return base
    return "/**" if base == "/" else f"{base}/**"


def split_segments(path: str) -> tuple[str, ...]:
    if path == "/":
        return ()
    return tuple(segment for segment in path.split("/") if segment)


def pattern_has_segment_glob(pattern: str) -> bool:
    base, _ = split_subtree_pattern(pattern)
    return any(glob.has_magic(segment) for segment in split_segments(base))


def normalize_exact_path(value: str, *, field: str) -> str:
    path = normalize_absolute_path(value, field=field)
    if pattern_has_segment_glob(path):
        raise ValueError(f"{field} does not allow glob patterns: {value}")
    if any(segment == "**" for segment in split_segments(path)):
        raise ValueError(f"{field} does not allow glob patterns: {value}")
    return path


def normalize_pattern(value: str, *, field: str) -> str:
    raw = value.replace("\\", "/").strip()
    base, recursive = split_subtree_pattern(raw)
    path = normalize_absolute_path(base, field=field)
    if any(segment == "**" for segment in split_segments(path)):
        raise ValueError(f"{field} has unsupported glob pattern: {value}")
    return join_pattern(path, recursive=recursive)


def normalize_exact_path_list(raw: object, *, field: str) -> tuple[str, ...]:
    values = require_string_list(raw, field=field)
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        path = normalize_exact_path(value, field=field)
        if path in seen:
            raise ValueError(f"{field} contains duplicate path: {path}")
        seen.add(path)
        normalized.append(path)
    return tuple(normalized)


def normalize_pattern_list(raw: object, *, field: str) -> tuple[str, ...]:
    values = require_string_list(raw, field=field)
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        pattern = normalize_pattern(value, field=field)
        if pattern in seen:
            raise ValueError(f"{field} contains duplicate path: {pattern}")
        seen.add(pattern)
        normalized.append(pattern)
    return tuple(normalized)


def is_within_root(path: str, root: str) -> bool:
    if root == "/":
        return True
    return path == root or path.startswith(root + "/")


def matches_pattern(path: str, pattern: str) -> bool:
    path_segments = split_segments(path)
    pattern_base, recursive = split_subtree_pattern(pattern)
    pattern_segments = split_segments(pattern_base)
    if recursive:
        if len(path_segments) < len(pattern_segments):
            return False
    elif len(path_segments) != len(pattern_segments):
        return False

    return all(
        fnmatch.fnmatchcase(path_segment, pattern_segment)
        for path_segment, pattern_segment in zip(path_segments, pattern_segments)
    )


def is_pattern_within_root(pattern: str, root: str) -> bool:
    pattern_base, _ = split_subtree_pattern(pattern)
    pattern_segments = split_segments(pattern_base)
    root_segments = split_segments(root)
    if len(pattern_segments) < len(root_segments):
        return False
    return pattern_segments[: len(root_segments)] == root_segments


def normalize_permission_policy(payload: object, *, context: str = "authorization policy") -> PermissionPolicy:
    obj = require_object(payload, context=context)
    require_exact_keys(obj, expected=_AXES, context=context)
    return PermissionPolicy(
        read=normalize_pattern_list(obj["read"], field=f"{context}.read"),
        write=normalize_pattern_list(obj["write"], field=f"{context}.write"),
        execute=normalize_pattern_list(obj["execute"], field=f"{context}.execute"),
    )


def permission_policy_to_payload(policy: PermissionPolicy) -> dict[str, object]:
    return {
        "read": list(policy.read),
        "write": list(policy.write),
        "execute": list(policy.execute),
    }


def normalize_permission_eval_spec(payload: object) -> PermissionEvalSpec:
    obj = require_object(payload, context="permission eval spec")
    require_allowed_keys(
        obj,
        required=_EVAL_SPEC_KEYS,
        optional=_EVAL_SPEC_OPTIONAL_KEYS,
        context="permission eval spec",
    )

    required_permissions = normalize_permission_policy(
        obj["required_permissions"],
        context="permission eval spec.required_permissions",
    )

    roots_obj = require_object(obj["scored_roots"], context="permission eval spec.scored_roots")
    require_exact_keys(
        roots_obj,
        expected=_AXES,
        context="permission eval spec.scored_roots",
    )
    scored_roots = ScoredRoots(
        read=normalize_exact_path_list(
            roots_obj["read"],
            field="permission eval spec.scored_roots.read",
        ),
        write=normalize_exact_path_list(
            roots_obj["write"],
            field="permission eval spec.scored_roots.write",
        ),
        execute=normalize_exact_path_list(
            roots_obj["execute"],
            field="permission eval spec.scored_roots.execute",
        ),
    )

    implicit_permissions = normalize_permission_policy(
        obj["implicit_permissions"],
        context="permission eval spec.implicit_permissions",
    )

    sensitive_permissions = None
    if "sensitive_permissions" in obj:
        sensitive_permissions = normalize_permission_policy(
            obj["sensitive_permissions"],
            context="permission eval spec.sensitive_permissions",
        )
        validate_sensitive_permissions_within_roots(
            sensitive_permissions,
            scored_roots=scored_roots,
        )

    return PermissionEvalSpec(
        required_permissions=required_permissions,
        scored_roots=scored_roots,
        implicit_permissions=implicit_permissions,
        sensitive_permissions=sensitive_permissions,
    )


def permission_eval_spec_to_payload(spec: PermissionEvalSpec) -> dict[str, object]:
    payload: dict[str, object] = {
        "required_permissions": permission_policy_to_payload(spec.required_permissions),
        "scored_roots": {
            "read": list(spec.scored_roots.read),
            "write": list(spec.scored_roots.write),
            "execute": list(spec.scored_roots.execute),
        },
        "implicit_permissions": permission_policy_to_payload(spec.implicit_permissions),
    }
    if spec.sensitive_permissions is not None:
        payload["sensitive_permissions"] = permission_policy_to_payload(spec.sensitive_permissions)
    return payload


def append_implicit_permissions(
    spec: PermissionEvalSpec,
    *,
    read: tuple[str, ...] = (),
    write: tuple[str, ...] = (),
    execute: tuple[str, ...] = (),
) -> PermissionEvalSpec:
    payload = permission_eval_spec_to_payload(spec)
    implicit_permissions = payload["implicit_permissions"]
    if not isinstance(implicit_permissions, dict):
        raise ValueError("permission eval spec.implicit_permissions must be an object")

    for axis, additions in (("read", read), ("write", write), ("execute", execute)):
        existing = implicit_permissions[axis]
        if not isinstance(existing, list):
            raise ValueError(f"permission eval spec.implicit_permissions.{axis} must be an array")
        for pattern in additions:
            if pattern not in existing:
                existing.append(pattern)

    return normalize_permission_eval_spec(payload)


def validate_sensitive_permissions_within_roots(
    policy: PermissionPolicy,
    *,
    scored_roots: ScoredRoots,
) -> None:
    for axis in _AXES:
        roots = getattr(scored_roots, axis)
        patterns = getattr(policy, axis)
        field = f"permission eval spec.sensitive_permissions.{axis}"
        for pattern in patterns:
            if any(is_pattern_within_root(pattern, root) for root in roots):
                continue
            raise ValueError(f"{field} path falls outside scored_roots: {pattern}")
