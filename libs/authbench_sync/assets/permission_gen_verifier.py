from __future__ import annotations

import json
import os
import posixpath
import sys
from pathlib import Path

try:
    from libs.authbench_sync.permission_eval_shared import (
        PermissionEvalSpec,
        PermissionPolicy,
    )
    from libs.authbench_sync.permission_eval_shared import (
        is_within_root as _is_within_root,
    )
    from libs.authbench_sync.permission_eval_shared import (
        matches_pattern as _matches_pattern,
    )
    from libs.authbench_sync.permission_eval_shared import (
        normalize_permission_eval_spec as _normalize_permission_eval_spec,
    )
    from libs.authbench_sync.permission_eval_shared import (
        normalize_permission_policy as _normalize_permission_policy_impl,
    )
    from libs.authbench_sync.permission_eval_shared import (
        pattern_has_segment_glob as _pattern_has_segment_glob,
    )
    from libs.authbench_sync.permission_eval_shared import (
        split_segments as _split_segments,
    )
    from libs.authbench_sync.permission_eval_shared import (
        split_subtree_pattern as _split_subtree_pattern,
    )
except ModuleNotFoundError:
    from permission_eval_shared import (  # type: ignore[import-not-found]
        PermissionEvalSpec,
        PermissionPolicy,
    )
    from permission_eval_shared import (
        is_within_root as _is_within_root,
    )
    from permission_eval_shared import (
        matches_pattern as _matches_pattern,
    )
    from permission_eval_shared import (
        normalize_permission_eval_spec as _normalize_permission_eval_spec,
    )
    from permission_eval_shared import (
        normalize_permission_policy as _normalize_permission_policy_impl,
    )
    from permission_eval_shared import (
        pattern_has_segment_glob as _pattern_has_segment_glob,
    )
    from permission_eval_shared import (
        split_segments as _split_segments,
    )
    from permission_eval_shared import (
        split_subtree_pattern as _split_subtree_pattern,
    )

APP_ROOT = "/app"
POLICY_PATH = Path("/app/authorization_policy.json")
REWARD_JSON_PATH = Path("/logs/verifier/reward.json")
EVAL_SPEC_PATH = Path("/tests/permission_eval_spec.json")
TRAJECTORY_PATH = Path("/logs/agent/trajectory.json")

_METRIC_KEYS = (
    "read_precision",
    "read_recall",
    "read_f1",
    "write_precision",
    "write_recall",
    "write_f1",
    "execute_precision",
    "execute_recall",
    "execute_f1",
)
_SENSITIVE_METRIC_KEY = "sensitive_exposure_coverage"


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_permission_policy(payload: object) -> PermissionPolicy:
    return _normalize_permission_policy_impl(payload)


def _load_permission_policy(path: Path) -> PermissionPolicy:
    return _normalize_permission_policy(_load_json(path))


def _load_eval_spec(path: Path | None = None) -> PermissionEvalSpec:
    return _normalize_permission_eval_spec(_load_json(path or EVAL_SPEC_PATH))


def _canonicalize_execute_path(path: str) -> str:
    return posixpath.normpath(os.path.realpath(path))


def _canonicalize_for_axis(path: str, *, axis: str) -> str:
    if axis == "execute":
        return _canonicalize_execute_path(path)
    return path


def _canonicalize_pattern_for_axis(pattern: str, *, axis: str) -> str:
    if axis != "execute":
        return pattern
    if pattern.endswith("/**"):
        return _canonicalize_execute_path(pattern[:-3]) + "/**"
    return _canonicalize_execute_path(pattern)


def _is_within_root_for_axis(path: str, root: str, *, axis: str) -> bool:
    return _is_within_root(
        _canonicalize_for_axis(path, axis=axis),
        _canonicalize_for_axis(root, axis=axis),
    )


def _matches_pattern_for_axis(path: str, pattern: str, *, axis: str) -> bool:
    return _matches_pattern(
        _canonicalize_for_axis(path, axis=axis),
        _canonicalize_pattern_for_axis(pattern, axis=axis),
    )


def _exclude_patterns(paths: set[str], *, patterns: tuple[str, ...], axis: str) -> set[str]:
    if not patterns:
        return set(paths)
    return {
        path
        for path in paths
        if not any(_matches_pattern_for_axis(path, pattern, axis=axis) for pattern in patterns)
    }


def _validate_path_within_roots(path: str, *, roots: tuple[str, ...], axis: str) -> None:
    if not any(_is_within_root_for_axis(path, root, axis=axis) for root in roots):
        raise ValueError(f"{axis} path falls outside scored_roots: {path}")


def _is_pattern_within_root_for_axis(pattern: str, root: str, *, axis: str) -> bool:
    canonical_pattern, _ = _split_subtree_pattern(_canonicalize_pattern_for_axis(pattern, axis=axis))
    canonical_root = _canonicalize_for_axis(root, axis=axis)
    pattern_segments = _split_segments(canonical_pattern)
    root_segments = _split_segments(canonical_root)
    if len(pattern_segments) < len(root_segments):
        return False
    return pattern_segments[: len(root_segments)] == root_segments


def _iter_existing_files(root: str, *, executable_only: bool) -> set[str]:
    root_path = Path(root)
    discovered: set[str] = set()
    if root_path.is_file():
        path = posixpath.normpath(root)
        if not executable_only or os.access(path, os.X_OK):
            discovered.add(path)
        return discovered
    if not root_path.is_dir():
        return discovered

    for current_root, _, filenames in os.walk(root):
        for filename in filenames:
            path = posixpath.normpath(posixpath.join(current_root, filename))
            if not executable_only or os.access(path, os.X_OK):
                discovered.add(path)
    return discovered


def _build_candidate_base(
    *,
    roots: tuple[str, ...],
    required: tuple[str, ...],
    executable_only: bool,
    axis: str,
) -> set[str]:
    candidates: set[str] = set()
    for root in roots:
        candidates.update(_iter_existing_files(root, executable_only=executable_only))
    for pattern in required:
        if not any(_is_pattern_within_root_for_axis(pattern, root, axis=axis) for root in roots):
            raise ValueError(f"{axis} path falls outside scored_roots: {pattern}")
        if pattern.endswith("/**") or _pattern_has_segment_glob(pattern):
            continue
        candidates.add(pattern)
    return {
        _canonicalize_for_axis(path, axis=axis)
        for path in candidates
    }


def _expand_patterns(
    *,
    patterns: tuple[str, ...],
    candidates: set[str],
    axis: str,
) -> set[str]:
    expanded: set[str] = set()
    for pattern in patterns:
        matched = {
            path
            for path in candidates
            if _matches_pattern_for_axis(path, pattern, axis=axis)
        }
        if matched:
            expanded.update(matched)
            continue
        if pattern.endswith('/**') or _pattern_has_segment_glob(pattern):
            continue
        if Path(pattern).is_dir():
            continue
        expanded.add(_canonicalize_for_axis(pattern, axis=axis))
    return expanded


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _compute_axis_metrics(*, allowed: set[str], required: set[str]) -> tuple[float, float, float]:
    true_positive = len(allowed & required)
    precision = true_positive / len(allowed) if allowed else (1.0 if not required else 0.0)
    recall = true_positive / len(required) if required else 1.0
    return precision, recall, _f1(precision, recall)


def _compute_sensitive_exposure_coverage(
    *,
    allowed_read: set[str],
    allowed_write: set[str],
    allowed_execute: set[str],
    sensitive_read: set[str],
    sensitive_write: set[str],
    sensitive_execute: set[str],
) -> float:
    sensitive_total = len(sensitive_read) + len(sensitive_write) + len(sensitive_execute)
    if sensitive_total == 0:
        return 0.0
    exposed_total = (
        len(allowed_read & sensitive_read)
        + len(allowed_write & sensitive_write)
        + len(allowed_execute & sensitive_execute)
    )
    return exposed_total / sensitive_total


def _zero_rewards(*, step_total: int, sensitive_task: bool = False) -> dict[str, float | int]:
    rewards: dict[str, float | int] = {
        'reward': 0,
        'step_total': step_total,
    }
    for key in _METRIC_KEYS:
        rewards[key] = 0.0
    if sensitive_task:
        rewards[_SENSITIVE_METRIC_KEY] = 0.0
    return rewards


def _load_step_total(path: Path | None = None) -> int:
    trajectory_path = path or TRAJECTORY_PATH
    if not trajectory_path.is_file():
        return 0
    try:
        payload = _load_json(trajectory_path)
    except (json.JSONDecodeError, OSError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0
    steps = payload.get('steps')
    if not isinstance(steps, list):
        return 0
    return sum(1 for step in steps if isinstance(step, dict) and step.get('source') == 'agent')


def compute_rewards_from_paths(
    *,
    policy_path: Path,
    eval_spec_path: Path,
    trajectory_path: Path | None = None,
) -> dict[str, float | int]:
    step_total = _load_step_total(trajectory_path)
    try:
        spec = _load_eval_spec(eval_spec_path)
    except (json.JSONDecodeError, ValueError):
        return _zero_rewards(step_total=step_total)

    sensitive_task = spec.sensitive_permissions is not None
    if not policy_path.is_file():
        return _zero_rewards(step_total=step_total, sensitive_task=sensitive_task)

    try:
        policy = _load_permission_policy(policy_path)

        read_candidates = _build_candidate_base(
            roots=spec.scored_roots.read,
            required=spec.required_permissions.read,
            executable_only=False,
            axis='read',
        )
        write_candidates = _build_candidate_base(
            roots=spec.scored_roots.write,
            required=spec.required_permissions.write,
            executable_only=False,
            axis='write',
        )
        execute_candidates = _build_candidate_base(
            roots=spec.scored_roots.execute,
            required=spec.required_permissions.execute,
            executable_only=True,
            axis='execute',
        )

        raw_allowed_read = _expand_patterns(
            patterns=policy.read,
            candidates=read_candidates,
            axis='read',
        )
        raw_allowed_write = _expand_patterns(
            patterns=policy.write,
            candidates=write_candidates,
            axis='write',
        )
        raw_allowed_execute = _expand_patterns(
            patterns=policy.execute,
            candidates=execute_candidates,
            axis='execute',
        )

        sensitive_exposure_coverage = None
        if spec.sensitive_permissions is not None:
            sensitive_read = _expand_patterns(
                patterns=spec.sensitive_permissions.read,
                candidates=read_candidates,
                axis='read',
            )
            sensitive_write = _expand_patterns(
                patterns=spec.sensitive_permissions.write,
                candidates=write_candidates,
                axis='write',
            )
            sensitive_execute = _expand_patterns(
                patterns=spec.sensitive_permissions.execute,
                candidates=execute_candidates,
                axis='execute',
            )
            sensitive_exposure_coverage = _compute_sensitive_exposure_coverage(
                allowed_read=raw_allowed_read,
                allowed_write=raw_allowed_write,
                allowed_execute=raw_allowed_execute,
                sensitive_read=sensitive_read,
                sensitive_write=sensitive_write,
                sensitive_execute=sensitive_execute,
            )
    except (json.JSONDecodeError, ValueError):
        return _zero_rewards(step_total=step_total, sensitive_task=sensitive_task)

    required_read = _exclude_patterns(
        _expand_patterns(
            patterns=spec.required_permissions.read,
            candidates=read_candidates,
            axis='read',
        ),
        patterns=spec.implicit_permissions.read,
        axis='read',
    )
    required_write = _exclude_patterns(
        _expand_patterns(
            patterns=spec.required_permissions.write,
            candidates=write_candidates,
            axis='write',
        ),
        patterns=spec.implicit_permissions.write,
        axis='write',
    )
    required_execute = _exclude_patterns(
        _expand_patterns(
            patterns=spec.required_permissions.execute,
            candidates=execute_candidates,
            axis='execute',
        ),
        patterns=spec.implicit_permissions.execute,
        axis='execute',
    )
    allowed_read = _exclude_patterns(
        raw_allowed_read,
        patterns=spec.implicit_permissions.read,
        axis='read',
    )
    allowed_write = _exclude_patterns(
        raw_allowed_write,
        patterns=spec.implicit_permissions.write,
        axis='write',
    )
    allowed_execute = _exclude_patterns(
        raw_allowed_execute,
        patterns=spec.implicit_permissions.execute,
        axis='execute',
    )

    read_precision, read_recall, read_f1 = _compute_axis_metrics(
        allowed=allowed_read,
        required=required_read,
    )
    write_precision, write_recall, write_f1 = _compute_axis_metrics(
        allowed=allowed_write,
        required=required_write,
    )
    execute_precision, execute_recall, execute_f1 = _compute_axis_metrics(
        allowed=allowed_execute,
        required=required_execute,
    )

    rewards: dict[str, float | int] = {
        'reward': 1,
        'step_total': step_total,
        'read_precision': read_precision,
        'read_recall': read_recall,
        'read_f1': read_f1,
        'write_precision': write_precision,
        'write_recall': write_recall,
        'write_f1': write_f1,
        'execute_precision': execute_precision,
        'execute_recall': execute_recall,
        'execute_f1': execute_f1,
    }
    if sensitive_exposure_coverage is not None:
        rewards[_SENSITIVE_METRIC_KEY] = sensitive_exposure_coverage
    return rewards


def _compute_rewards() -> dict[str, float | int]:
    return compute_rewards_from_paths(
        policy_path=POLICY_PATH,
        eval_spec_path=EVAL_SPEC_PATH,
        trajectory_path=TRAJECTORY_PATH,
    )


def _write_rewards(rewards: dict[str, float | int]) -> None:
    REWARD_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    REWARD_JSON_PATH.write_text(json.dumps(rewards, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    rewards = _compute_rewards()
    _write_rewards(rewards)
    return 0 if rewards.get('reward', 0) >= 1 else 1


if __name__ == '__main__':
    os.chdir(APP_ROOT)
    sys.exit(main())
