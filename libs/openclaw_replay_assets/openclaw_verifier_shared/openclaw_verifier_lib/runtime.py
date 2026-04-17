from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse


def build_config(
    agent_id: str,
    model_id: str,
    allowed_tools: list[str],
    workspace_path: Path,
    policy_guard_plugin_dir: Path | None = None,
    policy_guard_plugin_id: str | None = None,
    policy_guard_plugin_config: dict[str, object] | None = None,
    *,
    allow_bundled_skills: list[str] | None = None,
    base_url: str | None = None,
) -> dict[str, object]:
    provider_id, provider_model_id, primary_model_id = resolve_model_provider_config(
        model_id=model_id,
        base_url=base_url,
    )

    config = {
        "models": {
            "mode": "merge",
            "providers": {
                provider_id: {
                    "baseUrl": "${OPENAI_BASE_URL}",
                    "apiKey": {
                        "source": "env",
                        "provider": "default",
                        "id": "OPENAI_API_KEY",
                    },
                    "api": "openai-completions",
                    "models": [
                        {
                            "id": provider_model_id,
                            "name": provider_model_id,
                            "reasoning": False,
                            "input": ["text"],
                            "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                            "contextWindow": 128000,
                            "maxTokens": 8192,
                        }
                    ],
                }
            },
        },
        "agents": {
            "defaults": {
                "skipBootstrap": True,
                "model": {
                    "primary": primary_model_id,
                }
            },
            "list": [
                {
                    "id": agent_id,
                    "workspace": str(workspace_path),
                    "runtime": {"type": "embedded"},
                    "tools": {
                        "profile": "minimal",
                        "alsoAllow": allowed_tools,
                    },
                }
            ],
        },
        "tools": {
            "exec": {
                "host": "gateway",
                "security": "full",
                "ask": "off",
            }
        },
        "gateway": {
            "mode": "local",
            "bind": "loopback",
        },
    }

    if allow_bundled_skills is not None:
        config["skills"] = {
            "allowBundled": list(allow_bundled_skills),
        }

    if (
        policy_guard_plugin_dir is not None
        and policy_guard_plugin_id is not None
        and policy_guard_plugin_config is not None
    ):
        config["plugins"] = {
            "enabled": True,
            "allow": [policy_guard_plugin_id],
            "load": {
                "paths": [str(policy_guard_plugin_dir)],
            },
            "entries": {
                policy_guard_plugin_id: {
                    "enabled": True,
                    "config": policy_guard_plugin_config,
                },
            },
        }
    else:
        config["plugins"] = {"enabled": False}

    return config


def resolve_model_provider_config(
    *,
    model_id: str,
    base_url: str | None,
) -> tuple[str, str, str]:
    provider_model_id = _normalize_model_id(model_id)
    provider_id = _build_custom_provider_id(base_url)
    return provider_id, provider_model_id, f"{provider_id}/{provider_model_id}"


def _normalize_model_id(model_id: str) -> str:
    trimmed_model_id = model_id.strip()
    if not trimmed_model_id:
        raise ValueError("OpenClaw model_id must not be empty.")
    if "/" not in trimmed_model_id:
        return trimmed_model_id
    _, provider_model_id = trimmed_model_id.split("/", 1)
    provider_model_id = provider_model_id.strip()
    if not provider_model_id:
        raise ValueError("OpenClaw model_id must not be empty.")
    return provider_model_id


def _build_custom_provider_id(base_url: str | None) -> str:
    if not isinstance(base_url, str):
        return "custom"
    trimmed = base_url.strip()
    if not trimmed:
        return "custom"
    try:
        parsed = urlparse(trimmed)
        host = parsed.hostname or ""
        port = f"-{parsed.port}" if parsed.port else ""
        raw = f"custom-{host}{port}"
    except ValueError:
        raw = "custom"
    normalized = []
    last_was_dash = False
    for char in raw.lower():
        if char.isalnum():
            normalized.append(char)
            last_was_dash = False
            continue
        if not last_was_dash:
            normalized.append("-")
            last_was_dash = True
    slug = "".join(normalized).strip("-")
    return slug or "custom"
