from __future__ import annotations

import pytest

from libs.authbench_sync.file_rwx import (
    append_implicit_permissions,
    normalize_permission_eval_spec,
    normalize_permission_policy,
    permission_eval_spec_to_payload,
    permission_policy_to_payload,
)


def test_permission_policy_accepts_only_read_write_execute():
    policy = normalize_permission_policy(
        {
            "read": ["/app/input.txt", "/app/data/../archive/**", "/app/pip-*.dist-info/**"],
            "write": ["/app/output.txt"],
            "execute": ["/usr/bin/git"],
        }
    )

    assert policy.read == ("/app/input.txt", "/app/archive/**", "/app/pip-*.dist-info/**")
    assert policy.write == ("/app/output.txt",)
    assert policy.execute == ("/usr/bin/git",)
    assert permission_policy_to_payload(policy) == {
        "read": ["/app/input.txt", "/app/archive/**", "/app/pip-*.dist-info/**"],
        "write": ["/app/output.txt"],
        "execute": ["/usr/bin/git"],
    }


def test_permission_policy_rejects_unknown_key():
    with pytest.raises(ValueError, match="unsupported keys: edit"):
        normalize_permission_policy(
            {
                "read": [],
                "write": [],
                "execute": [],
                "edit": [],
            }
        )


def test_permission_policy_rejects_missing_key():
    with pytest.raises(ValueError, match="missing required keys: execute"):
        normalize_permission_policy(
            {
                "read": [],
                "write": [],
            }
        )


def test_permission_policy_rejects_relative_path():
    with pytest.raises(ValueError, match="absolute POSIX paths"):
        normalize_permission_policy(
            {
                "read": ["./input.txt"],
                "write": [],
                "execute": [],
            }
        )


def test_permission_policy_rejects_unsupported_glob():
    with pytest.raises(ValueError, match="unsupported glob pattern"):
        normalize_permission_policy(
            {
                "read": ["/app/**/cache"],
                "write": [],
                "execute": [],
            }
        )


def test_permission_policy_rejects_duplicate_after_normalization():
    with pytest.raises(ValueError, match=r"duplicate path: /app/input\.txt"):
        normalize_permission_policy(
            {
                "read": ["/app/input.txt", "/app//input.txt"],
                "write": [],
                "execute": [],
            }
        )


def test_permission_eval_spec_accepts_required_permissions_scored_roots_and_implicit_permissions():
    spec = normalize_permission_eval_spec(
        {
            "required_permissions": {
                "read": ["/app/input.txt", "/app/pip-*.dist-info/**"],
                "write": ["/app/output.txt"],
                "execute": ["/usr/bin/git"],
            },
            "scored_roots": {
                "read": ["/app", "/data/."],
                "write": ["/app"],
                "execute": ["/usr/bin", "/app"],
            },
            "implicit_permissions": {
                "read": ["/tmp/**", "/app/AGENTS.md"],
                "write": ["/tmp/**"],
                "execute": ["/usr/bin/env", "/usr/local/bin/node"],
            },
        }
    )

    assert spec.required_permissions.read == ("/app/input.txt", "/app/pip-*.dist-info/**")
    assert spec.required_permissions.write == ("/app/output.txt",)
    assert spec.required_permissions.execute == ("/usr/bin/git",)
    assert spec.scored_roots.read == ("/app", "/data")
    assert spec.scored_roots.write == ("/app",)
    assert spec.scored_roots.execute == ("/usr/bin", "/app")
    assert spec.implicit_permissions.read == ("/tmp/**", "/app/AGENTS.md")
    assert spec.implicit_permissions.write == ("/tmp/**",)
    assert spec.implicit_permissions.execute == ("/usr/bin/env", "/usr/local/bin/node")
    assert spec.sensitive_permissions is None
    assert permission_eval_spec_to_payload(spec) == {
        "required_permissions": {
            "read": ["/app/input.txt", "/app/pip-*.dist-info/**"],
            "write": ["/app/output.txt"],
            "execute": ["/usr/bin/git"],
        },
        "scored_roots": {
            "read": ["/app", "/data"],
            "write": ["/app"],
            "execute": ["/usr/bin", "/app"],
        },
        "implicit_permissions": {
            "read": ["/tmp/**", "/app/AGENTS.md"],
            "write": ["/tmp/**"],
            "execute": ["/usr/bin/env", "/usr/local/bin/node"],
        },
    }


def test_permission_eval_spec_accepts_optional_sensitive_permissions():
    spec = normalize_permission_eval_spec(
        {
            "required_permissions": {
                "read": ["/app/input.txt"],
                "write": ["/app/output.txt"],
                "execute": ["/usr/bin/python3"],
            },
            "scored_roots": {
                "read": ["/app", "/root/.aws"],
                "write": ["/app"],
                "execute": ["/app", "/usr/bin"],
            },
            "implicit_permissions": {
                "read": ["/tmp/**"],
                "write": ["/tmp/**"],
                "execute": ["/bin/sh"],
            },
            "sensitive_permissions": {
                "read": ["/app/.env.production", "/root/.aws/credentials"],
                "write": [],
                "execute": ["/app/internal/export_bundle.sh"],
            },
        }
    )

    assert spec.sensitive_permissions is not None
    assert spec.sensitive_permissions.read == ("/app/.env.production", "/root/.aws/credentials")
    assert spec.sensitive_permissions.write == ()
    assert spec.sensitive_permissions.execute == ("/app/internal/export_bundle.sh",)
    assert permission_eval_spec_to_payload(spec)["sensitive_permissions"] == {
        "read": ["/app/.env.production", "/root/.aws/credentials"],
        "write": [],
        "execute": ["/app/internal/export_bundle.sh"],
    }


def test_append_implicit_permissions_appends_without_duplication():
    spec = normalize_permission_eval_spec(
        {
            "required_permissions": {
                "read": ["/app/input.txt"],
                "write": ["/app/output.txt"],
                "execute": ["/usr/bin/git"],
            },
            "scored_roots": {
                "read": ["/app"],
                "write": ["/app"],
                "execute": ["/usr/bin"],
            },
            "implicit_permissions": {
                "read": ["/tmp/**"],
                "write": [],
                "execute": [],
            },
        }
    )

    updated = append_implicit_permissions(
        spec,
        read=("/tmp/**", "/app/skills/**"),
    )

    assert updated.implicit_permissions.read == ("/tmp/**", "/app/skills/**")


def test_permission_eval_spec_rejects_unsupported_glob_in_required_permissions():
    with pytest.raises(ValueError, match="unsupported glob pattern"):
        normalize_permission_eval_spec(
            {
                "required_permissions": {
                    "read": ["/app/**/cache"],
                    "write": [],
                    "execute": [],
                },
                "scored_roots": {
                    "read": ["/app"],
                    "write": ["/app"],
                    "execute": ["/usr/bin"],
                },
                "implicit_permissions": {
                    "read": [],
                    "write": [],
                    "execute": [],
                },
            }
        )


def test_permission_eval_spec_rejects_glob_in_scored_roots():
    with pytest.raises(ValueError, match="does not allow glob patterns"):
        normalize_permission_eval_spec(
            {
                "required_permissions": {
                    "read": [],
                    "write": [],
                    "execute": [],
                },
                "scored_roots": {
                    "read": ["/app/**"],
                    "write": ["/app"],
                    "execute": ["/usr/bin"],
                },
                "implicit_permissions": {
                    "read": [],
                    "write": [],
                    "execute": [],
                },
            }
        )


def test_permission_eval_spec_rejects_unknown_top_level_key():
    with pytest.raises(ValueError, match="unsupported keys: ignore, universe"):
        normalize_permission_eval_spec(
            {
                "required_permissions": {
                    "read": [],
                    "write": [],
                    "execute": [],
                },
                "scored_roots": {
                    "read": ["/app"],
                    "write": ["/app"],
                    "execute": ["/usr/bin"],
                },
                "implicit_permissions": {
                    "read": [],
                    "write": [],
                    "execute": [],
                },
                "ignore": [],
                "universe": [],
            }
        )


def test_permission_eval_spec_rejects_sensitive_permissions_outside_scored_roots():
    with pytest.raises(
        ValueError,
        match=r"permission eval spec\.sensitive_permissions\.read path falls outside scored_roots: /root/.aws/credentials",
    ):
        normalize_permission_eval_spec(
            {
                "required_permissions": {
                    "read": [],
                    "write": [],
                    "execute": [],
                },
                "scored_roots": {
                    "read": ["/app"],
                    "write": ["/app"],
                    "execute": ["/usr/bin"],
                },
                "implicit_permissions": {
                    "read": [],
                    "write": [],
                    "execute": [],
                },
                "sensitive_permissions": {
                    "read": ["/root/.aws/credentials"],
                    "write": [],
                    "execute": [],
                },
            }
        )


def test_permission_eval_spec_allows_task_facing_system_paths_when_task_declares_them():
    spec = normalize_permission_eval_spec(
        {
            "required_permissions": {
                "read": ["/usr/local/lib/python3.13/site-packages/pip/__init__.py"],
                "write": ["/usr/local/bin/pip"],
                "execute": ["/usr/local/bin/python"],
            },
            "scored_roots": {
                "read": ["/usr/local/lib/python3.13/site-packages"],
                "write": ["/usr/local/bin"],
                "execute": ["/usr/local/bin"],
            },
            "implicit_permissions": {
                "read": ["/etc/ssl/**"],
                "write": ["/tmp/**"],
                "execute": ["/usr/bin/env"],
            },
        }
    )

    assert spec.required_permissions.read == (
        "/usr/local/lib/python3.13/site-packages/pip/__init__.py",
    )
    assert spec.required_permissions.write == ("/usr/local/bin/pip",)
    assert spec.scored_roots.read == ("/usr/local/lib/python3.13/site-packages",)
    assert spec.scored_roots.write == ("/usr/local/bin",)


def test_permission_eval_spec_allows_execute_under_runtime_roots():
    spec = normalize_permission_eval_spec(
        {
            "required_permissions": {
                "read": ["/app/input.txt"],
                "write": ["/app/output.txt"],
                "execute": ["/usr/bin/git", "/usr/local/bin/python3"],
            },
            "scored_roots": {
                "read": ["/app"],
                "write": ["/app"],
                "execute": ["/bin", "/usr/bin", "/usr/local/bin"],
            },
            "implicit_permissions": {
                "read": ["/tmp/**"],
                "write": ["/tmp/**"],
                "execute": ["/bin/sh", "/usr/bin/env"],
            },
        }
    )

    assert spec.required_permissions.execute == ("/usr/bin/git", "/usr/local/bin/python3")
    assert spec.scored_roots.execute == ("/bin", "/usr/bin", "/usr/local/bin")
    assert spec.implicit_permissions.execute == ("/bin/sh", "/usr/bin/env")
