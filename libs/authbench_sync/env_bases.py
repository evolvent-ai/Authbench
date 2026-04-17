from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class BaseFamily:
    name: str
    plain_arg: str
    plain_default: str
    openclaw_arg: str
    openclaw_default: str


PYTHON_PY313_FAMILY = BaseFamily(
    name="python-py313",
    plain_arg="AUTHBENCH_PYTHON_PY313_PLAIN_BASE",
    plain_default="authbench-python-py313-plain-base:local",
    openclaw_arg="AUTHBENCH_PYTHON_PY313_OPENCLAW_BASE",
    openclaw_default="authbench-python-py313-openclaw-base:local",
)

TBENCH_PYTHON_PY313_FAMILY = BaseFamily(
    name="tbench-python-py313",
    plain_arg="AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE",
    plain_default="authbench-tbench-python-py313-plain-base:local",
    openclaw_arg="AUTHBENCH_TBENCH_PYTHON_PY313_OPENCLAW_BASE",
    openclaw_default="authbench-tbench-python-py313-openclaw-base:local",
)

PYTHON_PY311_FAMILY = BaseFamily(
    name="python-py311",
    plain_arg="AUTHBENCH_PYTHON_PY311_PLAIN_BASE",
    plain_default="authbench-python-py311-plain-base:local",
    openclaw_arg="AUTHBENCH_PYTHON_PY311_OPENCLAW_BASE",
    openclaw_default="authbench-python-py311-openclaw-base:local",
)

UBUNTU_PY_FAMILY = BaseFamily(
    name="ubuntu-py",
    plain_arg="AUTHBENCH_UBUNTU_PY_PLAIN_BASE",
    plain_default="authbench-ubuntu-py-plain-base:local",
    openclaw_arg="AUTHBENCH_UBUNTU_PY_OPENCLAW_BASE",
    openclaw_default="authbench-ubuntu-py-openclaw-base:local",
)

TBENCH_UBUNTU_PY_FAMILY = BaseFamily(
    name="tbench-ubuntu-py",
    plain_arg="AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE",
    plain_default="authbench-tbench-ubuntu-py-plain-base:local",
    openclaw_arg="AUTHBENCH_TBENCH_UBUNTU_PY_OPENCLAW_BASE",
    openclaw_default="authbench-tbench-ubuntu-py-openclaw-base:local",
)

_KNOWN_FAMILIES = (
    PYTHON_PY313_FAMILY,
    TBENCH_PYTHON_PY313_FAMILY,
    PYTHON_PY311_FAMILY,
    UBUNTU_PY_FAMILY,
    TBENCH_UBUNTU_PY_FAMILY,
)

_LOCAL_PREBUILT_DOCKER_COMPOSE_OVERRIDE = """services:
  main:
    pull_policy: never
"""

_TASK_PROXY_ARG_PREAMBLE = """ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ARG http_proxy
ARG https_proxy
ARG no_proxy"""

_TASK_APT_MIRROR_ARG_PREAMBLE = """ARG AUTHBENCH_UBUNTU_APT_MIRROR
ARG AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR
ARG AUTHBENCH_DEBIAN_APT_MIRROR
ARG AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR"""

_TASK_PIP_ARG_PREAMBLE = """ARG PIP_INDEX_URL
ARG PIP_EXTRA_INDEX_URL
ARG PIP_TRUSTED_HOST"""

_TASK_PROXY_ENV_PREAMBLE = """ENV HTTP_PROXY=${HTTP_PROXY} \\
    HTTPS_PROXY=${HTTPS_PROXY} \\
    NO_PROXY=${NO_PROXY} \\
    http_proxy=${http_proxy:-${HTTP_PROXY}} \\
    https_proxy=${https_proxy:-${HTTPS_PROXY}} \\
    no_proxy=${no_proxy:-${NO_PROXY}}"""

_TASK_PIP_ENV_PREAMBLE = """ENV PIP_INDEX_URL=${PIP_INDEX_URL} \\
    PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL} \\
    PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}"""

_TASK_APT_MIRROR_RUN_PREAMBLE = """RUN set -eu; \\
    ubuntu_mirror="${AUTHBENCH_UBUNTU_APT_MIRROR:-}"; \\
    ubuntu_security_mirror="${AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR:-}"; \\
    debian_mirror="${AUTHBENCH_DEBIAN_APT_MIRROR:-}"; \\
    debian_security_mirror="${AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR:-}"; \\
    if [ -n "$ubuntu_mirror" ] && [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \\
        ubuntu_mirror="${ubuntu_mirror%/}"; \\
        sed -i -E "s|URIs: https?://archive\\\\.ubuntu\\\\.com/ubuntu/?|URIs: ${ubuntu_mirror}|g" /etc/apt/sources.list.d/ubuntu.sources; \\
    fi; \\
    if [ -n "$ubuntu_security_mirror" ] && [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \\
        ubuntu_security_mirror="${ubuntu_security_mirror%/}"; \\
        sed -i -E "s|URIs: https?://security\\\\.ubuntu\\\\.com/ubuntu/?|URIs: ${ubuntu_security_mirror}|g" /etc/apt/sources.list.d/ubuntu.sources; \\
    fi; \\
    if [ -n "$debian_mirror" ] && [ -f /etc/apt/sources.list.d/debian.sources ]; then \\
        debian_mirror="${debian_mirror%/}"; \\
        sed -i -E "s|URIs: https?://deb\\\\.debian\\\\.org/debian/?|URIs: ${debian_mirror}|g" /etc/apt/sources.list.d/debian.sources; \\
    fi; \\
    if [ -n "$debian_security_mirror" ] && [ -f /etc/apt/sources.list.d/debian.sources ]; then \\
        debian_security_mirror="${debian_security_mirror%/}"; \\
        sed -i -E "s|URIs: https?://security\\\\.debian\\\\.org/debian-security/?|URIs: ${debian_security_mirror}|g" /etc/apt/sources.list.d/debian.sources; \\
    fi"""


def detect_base_family(dockerfile_text: str) -> BaseFamily:
    for family in _KNOWN_FAMILIES:
        if f"ARG {family.plain_arg}" in dockerfile_text or f"ARG {family.openclaw_arg}" in dockerfile_text:
            return family

    first_from = _extract_first_from(dockerfile_text)
    image_ref = first_from.removeprefix("FROM").strip().split()[0]

    if image_ref in {
        "python:3.13-slim-bookworm",
    }:
        return PYTHON_PY313_FAMILY
    if image_ref == "ghcr.io/laude-institute/t-bench/python-3-13:20250620":
        return TBENCH_PYTHON_PY313_FAMILY
    if image_ref in {
        "python:3.11-slim",
        "python:3.11-slim-bookworm",
    }:
        return PYTHON_PY311_FAMILY
    if image_ref in {
        "ubuntu:24.04",
    }:
        return UBUNTU_PY_FAMILY
    if image_ref == "ghcr.io/laude-institute/t-bench/ubuntu-24-04:20250624":
        return TBENCH_UBUNTU_PY_FAMILY

    known = ", ".join(family.name for family in _KNOWN_FAMILIES)
    raise ValueError(f"Unsupported task environment base image: {image_ref!r}. Known families: {known}")


def rewrite_task_dockerfile_to_shared_base(
    dockerfile_text: str,
    *,
    mode: str,
) -> str:
    if mode not in {"plain", "openclaw"}:
        raise ValueError(f"Unsupported shared-base mode: {mode}")

    family = detect_base_family(dockerfile_text)
    preamble, body = _split_dockerfile(dockerfile_text)
    if mode == "plain":
        arg_name = family.plain_arg
        default_ref = family.plain_default
    else:
        arg_name = family.openclaw_arg
        default_ref = family.openclaw_default

    body = _strip_leading_task_proxy_preamble(body)
    blocks: list[str] = []
    if preamble:
        preamble = _remove_shared_base_arg(preamble, arg_name)
        if preamble:
            blocks.append(preamble)
    blocks.append(f"ARG {arg_name}={default_ref}")
    blocks.append(f"FROM ${{{arg_name}}}")
    if body:
        blocks.append(body)
    return "\n\n".join(blocks).rstrip() + "\n"


def ensure_local_prebuilt_compose_override(
    task_path: str | Path,
    *,
    volume_mounts: list[tuple[str, str]] | None = None,
) -> Path:
    task_dir = Path(task_path).expanduser().resolve()
    compose_path = task_dir / "environment" / "docker-compose.yaml"
    existing_text = compose_path.read_text(encoding="utf-8") if compose_path.exists() else None
    compose_path.write_text(
        _build_local_prebuilt_compose_override(
            existing_text=existing_text,
            volume_mounts=volume_mounts,
        ),
        encoding="utf-8",
    )
    return compose_path


def _build_local_prebuilt_compose_override(
    *,
    existing_text: str | None = None,
    volume_mounts: list[tuple[str, str]] | None = None,
) -> str:
    if existing_text:
        payload = yaml.safe_load(existing_text) or {}
        if not isinstance(payload, dict):
            raise ValueError("docker-compose.yaml must parse to a mapping")
    else:
        payload = {}

    services = payload.get("services")
    if services is None:
        services = {}
        payload["services"] = services
    if not isinstance(services, dict):
        raise ValueError("docker-compose.yaml services must be a mapping")

    main = services.get("main")
    if main is None:
        main = {}
        services["main"] = main
    if not isinstance(main, dict):
        raise ValueError("docker-compose.yaml services.main must be a mapping")

    main["pull_policy"] = "never"

    if volume_mounts:
        existing_volumes = main.get("volumes")
        if existing_volumes is None:
            volumes_list: list[str] = []
        elif isinstance(existing_volumes, list):
            volumes_list = [str(item) for item in existing_volumes]
        else:
            raise ValueError("docker-compose.yaml services.main.volumes must be a list")

        for source, target in volume_mounts:
            mount = f"{source}:{target}:ro"
            if mount not in volumes_list:
                volumes_list.append(mount)
        main["volumes"] = volumes_list

    return yaml.safe_dump(payload, sort_keys=False)


def _extract_first_from(dockerfile_text: str) -> str:
    for raw_line in dockerfile_text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("ARG "):
            continue
        if stripped.startswith("FROM "):
            return stripped
        raise ValueError("Dockerfile must begin with comments/blank lines followed by FROM")
    raise ValueError("Dockerfile is empty")


def _split_dockerfile(dockerfile_text: str) -> tuple[str, str]:
    lines = dockerfile_text.splitlines()
    preamble: list[str] = []
    body_start: int | None = None

    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            preamble.append(raw_line)
            continue
        if stripped.startswith("ARG "):
            preamble.append(raw_line)
            continue
        if stripped.startswith("FROM "):
            body_start = index + 1
            break
        raise ValueError("Dockerfile must begin with comments/blank lines followed by FROM")

    if body_start is None:
        raise ValueError("Dockerfile is empty")

    body = "\n".join(lines[body_start:]).strip()
    preamble_text = "\n".join(preamble).strip()
    return preamble_text, body


def _remove_shared_base_arg(preamble_text: str, arg_name: str) -> str:
    kept_lines: list[str] = []
    proxy_arg_names = {
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "no_proxy",
        "AUTHBENCH_UBUNTU_APT_MIRROR",
        "AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR",
        "AUTHBENCH_DEBIAN_APT_MIRROR",
        "AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR",
        "PIP_INDEX_URL",
        "PIP_EXTRA_INDEX_URL",
        "PIP_TRUSTED_HOST",
    }
    for raw_line in preamble_text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith(f"ARG {arg_name}"):
            continue
        if any(stripped == f"ARG {name}" for name in proxy_arg_names):
            continue
        kept_lines.append(raw_line)
    return "\n".join(kept_lines).strip()


def _strip_leading_task_proxy_preamble(body_text: str) -> str:
    stripped = body_text.lstrip()

    changed = True
    while changed:
        changed = False
        for preamble in (
            _TASK_PROXY_ARG_PREAMBLE.strip(),
            _TASK_APT_MIRROR_ARG_PREAMBLE.strip(),
            _TASK_PIP_ARG_PREAMBLE.strip(),
            _TASK_PROXY_ENV_PREAMBLE.strip(),
            _TASK_PIP_ENV_PREAMBLE.strip(),
            _TASK_APT_MIRROR_RUN_PREAMBLE.strip(),
        ):
            if stripped.startswith(preamble):
                stripped = stripped[len(preamble) :].lstrip()
                changed = True

    return stripped
