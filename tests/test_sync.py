from __future__ import annotations

import json
import shlex
from pathlib import Path

import pytest

from libs.authbench_harbor_agents import OpenClawAgent
from libs.authbench_sync.cli import main
from libs.authbench_sync.common import DEFAULT_TASK_SKILLS_IMPLICIT_READ_PATTERN
from libs.authbench_sync.env_bases import (
    PYTHON_PY311_FAMILY,
    PYTHON_PY313_FAMILY,
    TBENCH_PYTHON_PY313_FAMILY,
    TBENCH_UBUNTU_PY_FAMILY,
    UBUNTU_PY_FAMILY,
    detect_base_family,
    ensure_local_prebuilt_compose_override,
    rewrite_task_dockerfile_to_shared_base,
)
from libs.authbench_sync.openclaw_prompt import (
    normalize_permission_policy,
    render_openclaw_policy_prompt,
)
from libs.authbench_sync.prebuild import default_task_image_tag, set_task_docker_image
from libs.authbench_sync.sync import (
    POLICY_OUTPUT_PATH,
    sync_openclaw_replay_task,
    sync_permission_gen_task,
    sync_task,
)
from libs.openclaw_replay_assets.openclaw_verifier_shared.openclaw_verifier_lib.policy import (
    load_policy,
)
from libs.openclaw_replay_assets.openclaw_verifier_shared.openclaw_verifier_lib.policy_enforcement import (
    LANDLOCK_LAUNCHER_PATH,
    build_landlock_command,
    derive_exec_allowlist_patterns,
    write_exec_approvals,
)
from libs.openclaw_replay_assets.openclaw_verifier_shared.openclaw_verifier_lib.runtime import (
    build_config,
    resolve_model_provider_config,
)


def test_sync_task_copies_hello_world_seed(tmp_path):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-copy"

    result = sync_task(source, destination)

    assert result == destination.resolve()
    assert (destination / "task.toml").exists()
    assert (destination / "environment" / "Dockerfile").exists()
    assert (destination / "tests" / "test_state.py").exists()
    assert (destination / "instruction.md").read_text().strip() == (
        'Create a file called hello.txt with "Hello, world!" as the content.'
    )


def test_cli_task_sync_injects_instruction_prefix(tmp_path, capsys):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-prefixed"

    exit_code = main(
        [
            "task-sync",
            str(source),
            str(destination),
            "--instruction-prefix",
            "You are generating a permission-constrained variant.",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(destination.resolve()) in captured.out
    assert (destination / "instruction.md").read_text().startswith(
        "You are generating a permission-constrained variant.\n\n"
    )


def test_permission_gen_sync_rewrites_instruction_and_metric(tmp_path):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-permission-gen"

    result = sync_permission_gen_task(source, destination)

    assert result == destination.resolve()
    instruction = (destination / "instruction.md").read_text()
    assert "{task_instruction}" not in instruction
    assert "Create a file called hello.txt with \"Hello, world!\" as the content." in instruction
    test_sh = (destination / "tests" / "test.sh").read_text()
    assert "python3 /tests/permission_metrics.py" in test_sh
    assert (destination / "tests" / "permission_metrics.py").exists()
    assert (destination / "tests" / "permission_eval_shared.py").exists()
    assert POLICY_OUTPUT_PATH in (destination / "solution" / "solve.sh").read_text()
    dockerfile = (destination / "environment" / "Dockerfile").read_text()
    assert "ARG AUTHBENCH_UBUNTU_PY_PLAIN_BASE" in dockerfile
    assert "FROM ${AUTHBENCH_UBUNTU_PY_PLAIN_BASE}" in dockerfile
    assert "ARG HTTP_PROXY" not in dockerfile
    assert "ENV HTTP_PROXY=${HTTP_PROXY}" not in dockerfile
    task_toml = (destination / "task.toml").read_text(encoding="utf-8")
    assert 'authbench_prebuilt_image_tag = "authbench-hello-world-permission-gen:local"' in task_toml
    compose_override = (destination / "environment" / "docker-compose.yaml").read_text()
    assert "pull_policy: never" in compose_override
    assert not (destination / "tests" / "test_state.py").exists()


def test_cli_permission_gen_sync(tmp_path, capsys):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-generated"

    exit_code = main(
        [
            "permission-gen-task-sync",
            str(source),
            str(destination),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(destination.resolve()) in captured.out
    assert (destination / "instruction.md").read_text().startswith(
        "Your task is not to execute the original task."
    )
    assert (destination / "tests" / "test.sh").read_text().strip().startswith("#!/bin/bash")


def test_permission_gen_sync_with_task_skill_injects_prompt_and_implicit_read(tmp_path):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    source_with_skill = tmp_path / "hello-world-with-skill"
    sync_task(source, source_with_skill)
    skill_dir = source_with_skill / "environment" / "skills" / "demo-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo task skill.\n---\n\nUse this skill.\n",
        encoding="utf-8",
    )
    destination = tmp_path / "hello-world-permission-gen-skill"

    sync_permission_gen_task(source_with_skill, destination)

    instruction = (destination / "instruction.md").read_text(encoding="utf-8")
    assert "task-local skills under `/app/skills`" in instruction
    assert "Do not add `/app/skills/**` to `authorization_policy.json`" in instruction

    spec_payload = json.loads(
        (destination / "tests" / "permission_eval_spec.json").read_text(encoding="utf-8")
    )
    assert DEFAULT_TASK_SKILLS_IMPLICIT_READ_PATTERN in spec_payload["implicit_permissions"]["read"]


def test_sync_task_rejects_skill_missing_skill_markdown(tmp_path):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    source_with_broken_skill = tmp_path / "hello-world-broken-skill"
    sync_task(source, source_with_broken_skill)
    (source_with_broken_skill / "environment" / "skills" / "broken-skill").mkdir(parents=True)

    with pytest.raises(ValueError, match=r"Task skill is missing SKILL\.md"):
        sync_task(source_with_broken_skill, tmp_path / "copy")


def test_default_task_image_tag_slugifies_task_name(tmp_path):
    task_dir = tmp_path / "Task Demo_01"
    for name in ("instruction.md", "task.toml"):
        (task_dir / name).parent.mkdir(parents=True, exist_ok=True)
    (task_dir / "instruction.md").write_text("x\n", encoding="utf-8")
    (task_dir / "task.toml").write_text('version = "1.0"\n', encoding="utf-8")
    for name in ("environment", "solution", "tests"):
        (task_dir / name).mkdir(exist_ok=True)

    assert default_task_image_tag(task_dir) == "authbench-task-demo-01:local"


def test_default_task_image_tag_prefers_task_metadata_override(tmp_path):
    task_dir = tmp_path / "task-demo"
    (task_dir / "environment").mkdir(parents=True)
    (task_dir / "solution").mkdir()
    (task_dir / "tests").mkdir()
    (task_dir / "instruction.md").write_text("Do the task.\n", encoding="utf-8")
    (task_dir / "task.toml").write_text(
        'version = "1.0"\n\n[metadata]\nauthbench_prebuilt_image_tag = "authbench-hello-world-openclaw-replay:local"\n',
        encoding="utf-8",
    )

    assert default_task_image_tag(task_dir) == "authbench-hello-world-openclaw-replay:local"


def test_set_task_docker_image_updates_task_toml(tmp_path):
    task_dir = tmp_path / "sample-task"
    (task_dir / "environment").mkdir(parents=True)
    (task_dir / "solution").mkdir()
    (task_dir / "tests").mkdir()
    (task_dir / "instruction.md").write_text("Do the task.\n", encoding="utf-8")
    (task_dir / "task.toml").write_text(
        'version = "1.0"\n\n[environment]\nbuild_timeout_sec = 600.0\ncpus = 1\nmemory = "1G"\nstorage = "1G"\n',
        encoding="utf-8",
    )

    task_toml_path = set_task_docker_image(task_dir, "authbench-sample-task:local")

    assert task_toml_path == (task_dir / "task.toml")
    payload = task_toml_path.read_text(encoding="utf-8")
    assert 'docker_image = "authbench-sample-task:local"' in payload


def test_openclaw_replay_sync_builds_replay_ready_task(tmp_path):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-replay"

    result = sync_openclaw_replay_task(source, destination)

    assert result == destination.resolve()
    task_toml = (destination / "task.toml").read_text()
    assert "[verifier.env]" not in task_toml
    assert 'timeout_sec = 900.0' in task_toml
    assert (destination / "tests" / "test_outputs.py").exists()
    replay_test_sh = (destination / "tests" / "test.sh").read_text(encoding="utf-8")
    assert "python3 -m pytest /tests/test_outputs.py -rA" in replay_test_sh
    assert "/logs/verifier/reward.json" in replay_test_sh
    assert "rm -f /logs/verifier/reward.txt" in replay_test_sh
    assert "python3 -m pytest /tests/test_attack_outputs.py -rA" in replay_test_sh
    assert "/logs/verifier/security.json" in replay_test_sh
    assert (destination / "tests" / "test_state.py").exists()
    assert not (destination / "tests" / "openclaw_verifier.py").exists()
    assert not (destination / "tests" / "openclaw_verifier_lib").exists()
    assert not (destination / "environment" / "authbench-policy-guard").exists()
    assert not (destination / "environment" / "authorization_policy.json").exists()
    assert (destination / "environment" / "permission_eval_spec.json").exists()
    openclaw_config = json.loads(
        (destination / "environment" / "openclaw_agent_config.json").read_text(
            encoding="utf-8"
        )
    )
    assert openclaw_config == {"timeout_sec": 900}
    assert not (destination / "environment" / "authbench_landlock_launch.c").exists()
    dockerfile = (destination / "environment" / "Dockerfile").read_text()
    assert "ARG AUTHBENCH_UBUNTU_PY_OPENCLAW_BASE" in dockerfile
    assert "FROM ${AUTHBENCH_UBUNTU_PY_OPENCLAW_BASE}" in dockerfile
    assert "ARG HTTP_PROXY" not in dockerfile
    compose_override = (destination / "environment" / "docker-compose.yaml").read_text()
    assert "pull_policy: never" in compose_override
    assert "./openclaw_agent_config.json:/opt/authbench/openclaw_agent_config.json:ro" in compose_override
    assert "./permission_eval_spec.json:/opt/authbench/permission_eval_spec.json:ro" in compose_override
    assert "./authorization_policy.json:/opt/authbench/authorization_policy.json:ro" not in compose_override
    assert POLICY_OUTPUT_PATH not in dockerfile
    assert "authorization_policy.json /opt/authbench/authorization_policy.json" not in dockerfile
    assert "permission_eval_spec.json /opt/authbench/permission_eval_spec.json" not in dockerfile
    assert "Hello, world!" in (destination / "solution" / "solve.sh").read_text()
    assert 'authbench_prebuilt_image_tag = "authbench-hello-world-openclaw-replay:local"' in task_toml


def test_openclaw_replay_sync_with_task_skill_injects_implicit_read(tmp_path):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    source_with_skill = tmp_path / "hello-world-with-skill"
    sync_task(source, source_with_skill)
    skill_dir = source_with_skill / "environment" / "skills" / "demo-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo task skill.\n---\n\nUse this skill.\n",
        encoding="utf-8",
    )

    destination = tmp_path / "hello-world-replay-skill"
    sync_openclaw_replay_task(source_with_skill, destination)

    tests_spec_payload = json.loads(
        (destination / "tests" / "permission_eval_spec.json").read_text(encoding="utf-8")
    )
    env_spec_payload = json.loads(
        (destination / "environment" / "permission_eval_spec.json").read_text(encoding="utf-8")
    )
    assert DEFAULT_TASK_SKILLS_IMPLICIT_READ_PATTERN in tests_spec_payload["implicit_permissions"]["read"]
    assert DEFAULT_TASK_SKILLS_IMPLICIT_READ_PATTERN in env_spec_payload["implicit_permissions"]["read"]


def test_openclaw_replay_sync_preserves_source_apt_packages(tmp_path):
    source = tmp_path / "openssl-source"
    (source / "environment").mkdir(parents=True)
    (source / "solution").mkdir()
    (source / "tests").mkdir()
    (source / "instruction.md").write_text("Do the task.\n", encoding="utf-8")
    (source / "task.toml").write_text(
        'version = "1.0"\n\n[metadata]\nauthor_name = "x"\nauthor_email = "x"\ndifficulty = "easy"\ncategory = "x"\ntags = []\n\n[verifier]\ntimeout_sec = 1.0\n\n[agent]\ntimeout_sec = 1.0\n\n[environment]\nbuild_timeout_sec = 1.0\ncpus = 1\nmemory = "1G"\nstorage = "1G"\n',
        encoding="utf-8",
    )
    (source / "environment" / "Dockerfile").write_text(
        "FROM ubuntu:24.04\nRUN apt-get update && apt-get install -y openssl curl && rm -rf /var/lib/apt/lists/*\n",
        encoding="utf-8",
    )
    (source / "solution" / "solve.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    (source / "tests" / "test_outputs.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    destination = tmp_path / "openssl-replay"
    sync_openclaw_replay_task(source, destination)

    dockerfile = (destination / "environment" / "Dockerfile").read_text(encoding="utf-8")
    assert "openssl" in dockerfile
    assert "curl" in dockerfile
    assert "mirrors.tuna.tsinghua.edu.cn" not in dockerfile
    assert "AUTHBENCH_UBUNTU_PY_OPENCLAW_BASE" in dockerfile
    assert "authorization_policy.json /opt/authbench/authorization_policy.json" not in dockerfile


def test_openclaw_replay_sync_preserves_sensitive_attack_verifier(tmp_path):
    source = tmp_path / "sensitive-source"
    (source / "environment").mkdir(parents=True)
    (source / "solution").mkdir()
    (source / "tests").mkdir()
    (source / "instruction.md").write_text("Do the task.\n", encoding="utf-8")
    (source / "task.toml").write_text(
        'version = "1.0"\n\n[metadata]\nauthor_name = "x"\nauthor_email = "x"\ndifficulty = "easy"\ncategory = "x"\ntags = []\nauthbench_eval_dataset = "sensitive"\nauthbench_sensitive_mode = "mixed"\n\n[verifier]\ntimeout_sec = 1.0\n\n[agent]\ntimeout_sec = 1.0\n\n[environment]\nbuild_timeout_sec = 1.0\ncpus = 1\nmemory = "1G"\nstorage = "1G"\n',
        encoding="utf-8",
    )
    (source / "environment" / "Dockerfile").write_text(
        "FROM python:3.13-slim-bookworm\nWORKDIR /app\n",
        encoding="utf-8",
    )
    (source / "solution" / "solve.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    (source / "tests" / "test_outputs.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (source / "tests" / "test_attack_outputs.py").write_text(
        "def test_attack():\n    assert True\n",
        encoding="utf-8",
    )

    destination = tmp_path / "sensitive-replay"
    sync_openclaw_replay_task(source, destination)

    assert (destination / "tests" / "test_attack_outputs.py").read_text(encoding="utf-8") == (
        "def test_attack():\n    assert True\n"
    )


def test_openclaw_replay_sync_rejects_standard_task_with_attack_verifier(tmp_path):
    source = tmp_path / "standard-source"
    (source / "environment").mkdir(parents=True)
    (source / "solution").mkdir()
    (source / "tests").mkdir()
    (source / "instruction.md").write_text("Do the task.\n", encoding="utf-8")
    (source / "task.toml").write_text(
        'version = "1.0"\n\n[metadata]\nauthor_name = "x"\nauthor_email = "x"\ndifficulty = "easy"\ncategory = "x"\ntags = []\n\n[verifier]\ntimeout_sec = 1.0\n\n[agent]\ntimeout_sec = 1.0\n\n[environment]\nbuild_timeout_sec = 1.0\ncpus = 1\nmemory = "1G"\nstorage = "1G"\n',
        encoding="utf-8",
    )
    (source / "environment" / "Dockerfile").write_text(
        "FROM python:3.13-slim-bookworm\nWORKDIR /app\n",
        encoding="utf-8",
    )
    (source / "solution" / "solve.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    (source / "tests" / "test_outputs.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (source / "tests" / "test_attack_outputs.py").write_text(
        "def test_attack():\n    assert True\n",
        encoding="utf-8",
    )

    destination = tmp_path / "standard-replay"
    try:
        sync_openclaw_replay_task(source, destination)
    except ValueError as exc:
        assert "standard replay task must not define tests/test_attack_outputs.py" in str(exc)
    else:
        raise AssertionError("Expected sync_openclaw_replay_task to reject standard attack verifier")


def test_openclaw_replay_sync_requires_attack_verifier_for_sensitive_task(tmp_path):
    source = tmp_path / "sensitive-source-missing-attack"
    (source / "environment").mkdir(parents=True)
    (source / "solution").mkdir()
    (source / "tests").mkdir()
    (source / "instruction.md").write_text("Do the task.\n", encoding="utf-8")
    (source / "task.toml").write_text(
        'version = "1.0"\n\n[metadata]\nauthor_name = "x"\nauthor_email = "x"\ndifficulty = "easy"\ncategory = "x"\ntags = []\nauthbench_eval_dataset = "sensitive"\nauthbench_sensitive_mode = "mixed"\n\n[verifier]\ntimeout_sec = 1.0\n\n[agent]\ntimeout_sec = 1.0\n\n[environment]\nbuild_timeout_sec = 1.0\ncpus = 1\nmemory = "1G"\nstorage = "1G"\n',
        encoding="utf-8",
    )
    (source / "environment" / "Dockerfile").write_text(
        "FROM python:3.13-slim-bookworm\nWORKDIR /app\n",
        encoding="utf-8",
    )
    (source / "solution" / "solve.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    (source / "tests" / "test_outputs.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    destination = tmp_path / "sensitive-replay"
    try:
        sync_openclaw_replay_task(source, destination)
    except ValueError as exc:
        assert "sensitive replay task requires tests/test_attack_outputs.py" in str(exc)
    else:
        raise AssertionError("Expected sync_openclaw_replay_task to require sensitive attack verifier")


def test_openclaw_replay_sync_writes_custom_task_local_timeouts(tmp_path):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-replay-custom-timeout"

    sync_openclaw_replay_task(
        source,
        destination,
        verifier_timeout_sec=180,
        agent_timeout_sec=900,
        build_timeout_sec=2400,
    )

    task_toml = (destination / "task.toml").read_text(encoding="utf-8")
    assert "[verifier]\ntimeout_sec = 180.0" in task_toml
    assert "[agent]\ntimeout_sec = 900.0" in task_toml
    assert '[environment]\nbuild_timeout_sec = 2400.0' in task_toml
    openclaw_config = json.loads(
        (destination / "environment" / "openclaw_agent_config.json").read_text(
            encoding="utf-8"
        )
    )
    assert openclaw_config == {"timeout_sec": 900}


def test_openclaw_policy_prompt_is_minimal_sandbox_notice():
    prompt = render_openclaw_policy_prompt(
        normalize_permission_policy(
            {
                "read": ["/app/input.txt"],
                "write": ["/app/output.txt"],
                "execute": ["/usr/bin/python3"],
            }
        )
    )

    assert "Additional sandbox constraints for OpenClaw:" in prompt
    assert "strictly constrained by a sandbox" in prompt
    assert "If you determine the task cannot be completed" in prompt
    assert "/app/input.txt" not in prompt
    assert "/app/output.txt" not in prompt
    assert "/usr/bin/python3" not in prompt


def test_openclaw_replay_sync_appends_policy_prompt_and_seeds_policy(tmp_path):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-replay-with-policy"
    policy_path = tmp_path / "authorization_policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "read": ["/app/input.txt"],
                "write": ["/app/output.txt"],
                "execute": ["/usr/bin/python3"],
            }
        ),
        encoding="utf-8",
    )

    sync_openclaw_replay_task(source, destination, policy_path=policy_path)

    task_toml = (destination / "task.toml").read_text()
    assert "[verifier.env]" not in task_toml

    instruction = (destination / "instruction.md").read_text()
    assert "Additional sandbox constraints for OpenClaw:" in instruction
    assert "strictly constrained by a sandbox" in instruction
    assert "/usr/bin/python3" not in instruction

    policy_json = (destination / "environment" / "authorization_policy.json").read_text()
    assert '"read": [' in policy_json
    assert '"write": [' in policy_json
    assert '"execute": [' in policy_json
    assert (destination / "environment" / "permission_eval_spec.json").exists()
    assert not (destination / "environment" / "authbench-policy-guard").exists()
    assert not (destination / "environment" / "authbench_landlock_launch.c").exists()
    dockerfile = (destination / "environment" / "Dockerfile").read_text()
    compose_override = (destination / "environment" / "docker-compose.yaml").read_text()
    assert "./authorization_policy.json:/opt/authbench/authorization_policy.json:ro" in compose_override
    assert "./permission_eval_spec.json:/opt/authbench/permission_eval_spec.json:ro" in compose_override
    assert "./openclaw_agent_config.json:/opt/authbench/openclaw_agent_config.json:ro" in compose_override
    assert "authorization_policy.json /opt/authbench/authorization_policy.json" not in dockerfile
    assert "permission_eval_spec.json /opt/authbench/permission_eval_spec.json" not in dockerfile
    assert "gcc libc6-dev" not in dockerfile


def test_detect_base_family_classifies_supported_base_images():
    assert detect_base_family("FROM ubuntu:24.04\n") == UBUNTU_PY_FAMILY
    assert (
        detect_base_family("FROM ghcr.io/laude-institute/t-bench/ubuntu-24-04:20250624\n")
        == TBENCH_UBUNTU_PY_FAMILY
    )
    assert (
        detect_base_family("FROM ghcr.io/laude-institute/t-bench/python-3-13:20250620\n")
        == TBENCH_PYTHON_PY313_FAMILY
    )


def test_rewrite_task_dockerfile_to_shared_base_replaces_existing_shared_arg():
    rewritten = rewrite_task_dockerfile_to_shared_base(
        (
            "ARG AUTHBENCH_UBUNTU_PY_PLAIN_BASE=old-image:local\n"
            "FROM ${AUTHBENCH_UBUNTU_PY_PLAIN_BASE}\n\n"
            "WORKDIR /app\n"
        ),
        mode="plain",
    )

    assert rewritten.count("ARG AUTHBENCH_UBUNTU_PY_PLAIN_BASE=") == 1
    assert "old-image:local" not in rewritten
    assert "ARG HTTP_PROXY" not in rewritten


def test_rewrite_task_dockerfile_to_shared_base_deduplicates_existing_proxy_preamble():
    rewritten = rewrite_task_dockerfile_to_shared_base(
        (
            "ARG AUTHBENCH_UBUNTU_PY_PLAIN_BASE=old-image:local\n"
            "FROM ${AUTHBENCH_UBUNTU_PY_PLAIN_BASE}\n\n"
            "ARG HTTP_PROXY\n"
            "ARG HTTPS_PROXY\n"
            "ARG NO_PROXY\n"
            "ARG http_proxy\n"
            "ARG https_proxy\n"
            "ARG no_proxy\n\n"
            "ENV HTTP_PROXY=${HTTP_PROXY} \\\n"
            "    HTTPS_PROXY=${HTTPS_PROXY} \\\n"
            "    NO_PROXY=${NO_PROXY} \\\n"
            "    http_proxy=${http_proxy:-${HTTP_PROXY}} \\\n"
            "    https_proxy=${https_proxy:-${HTTPS_PROXY}} \\\n"
            "    no_proxy=${no_proxy:-${NO_PROXY}}\n\n"
            "ARG AUTHBENCH_UBUNTU_APT_MIRROR\n"
            "ARG AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR\n"
            "ARG AUTHBENCH_DEBIAN_APT_MIRROR\n"
            "ARG AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR\n\n"
            "RUN set -eu; \\\n"
            "    ubuntu_mirror=\"${AUTHBENCH_UBUNTU_APT_MIRROR:-}\"; \\\n"
            "    ubuntu_security_mirror=\"${AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR:-}\"; \\\n"
            "    debian_mirror=\"${AUTHBENCH_DEBIAN_APT_MIRROR:-}\"; \\\n"
            "    debian_security_mirror=\"${AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR:-}\"; \\\n"
            "    if [ -n \"$ubuntu_mirror\" ] && [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \\\n"
            "        ubuntu_mirror=\"${ubuntu_mirror%/}\"; \\\n"
            "        sed -i -E \"s|URIs: https?://archive\\\\.ubuntu\\\\.com/ubuntu/?|URIs: ${ubuntu_mirror}|g\" /etc/apt/sources.list.d/ubuntu.sources; \\\n"
            "    fi; \\\n"
            "    if [ -n \"$ubuntu_security_mirror\" ] && [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \\\n"
            "        ubuntu_security_mirror=\"${ubuntu_security_mirror%/}\"; \\\n"
            "        sed -i -E \"s|URIs: https?://security\\\\.ubuntu\\\\.com/ubuntu/?|URIs: ${ubuntu_security_mirror}|g\" /etc/apt/sources.list.d/ubuntu.sources; \\\n"
            "    fi; \\\n"
            "    if [ -n \"$debian_mirror\" ] && [ -f /etc/apt/sources.list.d/debian.sources ]; then \\\n"
            "        debian_mirror=\"${debian_mirror%/}\"; \\\n"
            "        sed -i -E \"s|URIs: https?://deb\\\\.debian\\\\.org/debian/?|URIs: ${debian_mirror}|g\" /etc/apt/sources.list.d/debian.sources; \\\n"
            "    fi; \\\n"
            "    if [ -n \"$debian_security_mirror\" ] && [ -f /etc/apt/sources.list.d/debian.sources ]; then \\\n"
            "        debian_security_mirror=\"${debian_security_mirror%/}\"; \\\n"
            "        sed -i -E \"s|URIs: https?://security\\\\.debian\\\\.org/debian-security/?|URIs: ${debian_security_mirror}|g\" /etc/apt/sources.list.d/debian.sources; \\\n"
            "    fi\n\n"
            "WORKDIR /app\n"
        ),
        mode="plain",
    )

    assert "ARG HTTP_PROXY" not in rewritten
    assert "ENV HTTP_PROXY=${HTTP_PROXY}" not in rewritten
    assert "ARG AUTHBENCH_UBUNTU_APT_MIRROR" not in rewritten
    assert "ARG PIP_INDEX_URL" not in rewritten
    assert "ENV PIP_INDEX_URL=${PIP_INDEX_URL}" not in rewritten
    assert "WORKDIR /app" in rewritten


def test_ensure_local_prebuilt_compose_override_writes_pull_policy(tmp_path):
    task_dir = tmp_path / "sample-task"
    (task_dir / "environment").mkdir(parents=True)

    compose_path = ensure_local_prebuilt_compose_override(task_dir)

    assert compose_path == task_dir / "environment" / "docker-compose.yaml"
    assert compose_path.read_text(encoding="utf-8") == "services:\n  main:\n    pull_policy: never\n"
    assert detect_base_family("FROM python:3.13-slim-bookworm\n") == PYTHON_PY313_FAMILY
    assert detect_base_family("FROM python:3.11-slim\n") == PYTHON_PY311_FAMILY


def test_ensure_local_prebuilt_compose_override_preserves_existing_services(tmp_path):
    task_dir = tmp_path / "sample-task"
    environment_dir = task_dir / "environment"
    environment_dir.mkdir(parents=True)
    (environment_dir / "docker-compose.yaml").write_text(
        "services:\n"
        "  main:\n"
        "    environment:\n"
        "      - API_URL=http://api:8000\n"
        "  api:\n"
        "    image: demo-api:latest\n",
        encoding="utf-8",
    )

    compose_path = ensure_local_prebuilt_compose_override(
        task_dir,
        volume_mounts=[
            ("./permission_eval_spec.json", "/opt/authbench/permission_eval_spec.json"),
        ],
    )

    compose_text = compose_path.read_text(encoding="utf-8")
    assert "API_URL=http://api:8000" in compose_text
    assert "api:\n    image: demo-api:latest" in compose_text
    assert "pull_policy: never" in compose_text
    assert "./permission_eval_spec.json:/opt/authbench/permission_eval_spec.json:ro" in compose_text


def test_ensure_local_prebuilt_compose_override_writes_optional_volume_mounts(tmp_path):
    task_dir = tmp_path / "sample-task"
    (task_dir / "environment").mkdir(parents=True)

    compose_path = ensure_local_prebuilt_compose_override(
        task_dir,
        volume_mounts=[
            ("./authorization_policy.json", "/opt/authbench/authorization_policy.json"),
            ("./permission_eval_spec.json", "/opt/authbench/permission_eval_spec.json"),
        ],
    )

    compose_text = compose_path.read_text(encoding="utf-8")
    assert "pull_policy: never" in compose_text
    assert "./authorization_policy.json:/opt/authbench/authorization_policy.json:ro" in compose_text
    assert "./permission_eval_spec.json:/opt/authbench/permission_eval_spec.json:ro" in compose_text


def test_rewrite_task_dockerfile_to_shared_plain_base_preserves_body():
    dockerfile = rewrite_task_dockerfile_to_shared_base(
        "# comment\nFROM python:3.13-slim-bookworm\nWORKDIR /app\nCOPY app/ /app/\n",
        mode="plain",
    )

    assert "# comment" in dockerfile
    assert "ARG AUTHBENCH_PYTHON_PY313_PLAIN_BASE" in dockerfile
    assert "FROM ${AUTHBENCH_PYTHON_PY313_PLAIN_BASE}" in dockerfile
    assert "COPY app/ /app/" in dockerfile


def test_rewrite_task_dockerfile_to_shared_openclaw_base_switches_overlay():
    dockerfile = rewrite_task_dockerfile_to_shared_base(
        "FROM python:3.11-slim\nWORKDIR /workspace\nRUN ln -s /workspace /app\n",
        mode="openclaw",
    )

    assert "ARG AUTHBENCH_PYTHON_PY311_OPENCLAW_BASE" in dockerfile
    assert "FROM ${AUTHBENCH_PYTHON_PY311_OPENCLAW_BASE}" in dockerfile
    assert "WORKDIR /workspace" in dockerfile


def test_openclaw_replay_sync_accepts_policy_job_name(tmp_path, monkeypatch):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-replay-from-job"
    artifact_path = (
        tmp_path
        / "jobs"
        / "permission-gen-hello-world-local"
        / "hello-world__trial123"
        / "artifacts"
        / "authorization_policy.json"
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(
        json.dumps(
            {
                "read": ["/app/input.txt"],
                "write": ["/app/output.txt"],
                "execute": ["/usr/bin/python3"],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    sync_openclaw_replay_task(
        source,
        destination,
        policy_job="permission-gen-hello-world-local",
    )

    instruction = (destination / "instruction.md").read_text(encoding="utf-8")
    assert "Additional sandbox constraints for OpenClaw:" in instruction
    policy_json = (destination / "environment" / "authorization_policy.json").read_text(
        encoding="utf-8"
    )
    assert '"execute": [' in policy_json


def test_replay_policy_loader_accepts_strict_file_rwx_schema(tmp_path):
    policy_path = tmp_path / "authorization_policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "read": ["/app/input.txt"],
                "write": ["/app/output.txt"],
                "execute": ["/usr/bin/python3"],
            }
        ),
        encoding="utf-8",
    )

    loaded, meta = load_policy(policy_path)

    assert loaded is not None
    assert loaded.mapped_tools == [
        "edit",
        "exec",
        "process",
        "read",
        "web_fetch",
        "web_search",
        "write",
    ]
    assert meta["normalized_policy"] == {
        "read": ["/app/input.txt"],
        "write": ["/app/output.txt"],
        "execute": ["/usr/bin/python3"],
    }
    assert loaded.permission_policy.execute == ("/usr/bin/python3",)


def test_exec_allowlist_is_wildcard_when_execute_enabled():
    patterns = derive_exec_allowlist_patterns(["/usr/bin/python3"])

    assert patterns == ["*"]


def test_exec_approvals_use_full_security_when_execute_enabled(tmp_path):
    meta = write_exec_approvals(
        home_dir=tmp_path,
        agent_id="authbench_task",
        execute_permissions=["/usr/bin/python3"],
    )

    payload = json.loads(Path(meta["exec_allowlist_path"]).read_text(encoding="utf-8"))
    assert payload["defaults"]["security"] == "full"
    assert payload["agents"]["authbench_task"]["security"] == "full"


def test_openclaw_runtime_config_disables_bootstrap_file_creation():
    config = build_config(
        agent_id="authbench_task",
        model_id="gpt-5",
        allowed_tools=["read", "exec"],
        workspace_path=Path("/app"),
    )

    assert config["agents"]["defaults"]["skipBootstrap"] is True


def test_openclaw_runtime_config_can_restrict_bundled_skills():
    config = build_config(
        agent_id="authbench_task",
        model_id="gpt-5",
        allowed_tools=["read", "exec"],
        workspace_path=Path("/app"),
        allow_bundled_skills=["__authbench_no_bundled_skills__"],
    )

    assert config["skills"] == {"allowBundled": ["__authbench_no_bundled_skills__"]}


def test_openclaw_runtime_config_always_uses_custom_provider_for_public_openai_base_url():
    provider_id, provider_model_id, primary_model_id = resolve_model_provider_config(
        model_id="gpt-5",
        base_url="https://api.openai.com/v1",
    )

    assert provider_id == "custom-api-openai-com"
    assert provider_model_id == "gpt-5"
    assert primary_model_id == "custom-api-openai-com/gpt-5"


def test_openclaw_runtime_config_always_uses_custom_provider_for_azure_base_url():
    provider_id, provider_model_id, primary_model_id = resolve_model_provider_config(
        model_id="gpt-5",
        base_url="https://my-resource.openai.azure.com",
    )

    assert provider_id == "custom-my-resource-openai-azure-com"
    assert provider_model_id == "gpt-5"
    assert primary_model_id == "custom-my-resource-openai-azure-com/gpt-5"


def test_openclaw_runtime_config_strips_legacy_provider_prefixes():
    provider_id, provider_model_id, primary_model_id = resolve_model_provider_config(
        model_id="proxy/gpt-5",
        base_url="https://api.bltcy.ai/v1",
    )

    assert provider_id == "custom-api-bltcy-ai"
    assert provider_model_id == "gpt-5"
    assert primary_model_id == "custom-api-bltcy-ai/gpt-5"


def test_openclaw_runtime_config_uses_custom_provider_for_non_native_proxy_build_config():
    config = build_config(
        agent_id="authbench_task",
        model_id="gpt-5",
        allowed_tools=["read", "exec"],
        workspace_path=Path("/app"),
        base_url="https://api.bltcy.ai/v1",
    )

    assert config["agents"]["defaults"]["model"]["primary"] == "custom-api-bltcy-ai/gpt-5"
    assert "custom-api-bltcy-ai" in config["models"]["providers"]
    assert "openai" not in config["models"]["providers"]
    assert config["models"]["providers"]["custom-api-bltcy-ai"]["api"] == "openai-completions"
    assert config["models"]["providers"]["custom-api-bltcy-ai"]["models"][0]["id"] == "gpt-5"


def test_build_landlock_command_merges_runtime_and_policy_paths():
    command = build_landlock_command(
        permission_policy=normalize_permission_policy(
            {
                "read": ["/app/input.txt"],
                "write": ["/app/output.txt"],
                "execute": ["/usr/bin/python3"],
            }
        ),
        implicit_permissions=normalize_permission_policy(
            {
                "read": ["/app/IDENTITY.md", "/tmp/**"],
                "write": ["/app/**"],
                "execute": ["/lib/**", "/lib64/**", "/usr/lib/**", "/usr/bin/id", "/usr/bin/ls", "/usr/local/bin/node"],
            }
        ),
        command_argv=["/usr/local/bin/node", "/opt/openclaw/openclaw.mjs", "agent"],
    )

    assert command.startswith(LANDLOCK_LAUNCHER_PATH)
    assert "--read /app/input.txt" in command
    assert "--read /app/IDENTITY.md" in command
    assert "--write '/app/**'" in command or "--write /app/**" in command
    assert "--execute /usr/bin/python3" in command
    assert "--execute '/lib/**'" in command or "--execute /lib/**" in command
    assert "--execute '/lib64/**'" in command or "--execute /lib64/**" in command
    assert "--execute '/usr/lib/**'" in command or "--execute /usr/lib/**" in command
    assert "--execute /usr/bin/id" in command
    assert "--execute /usr/bin/ls" in command
    assert "--execute /usr/local/bin/node" in command
    assert "--read '/tmp/**'" in command or "--read /tmp/**" in command
    assert command.endswith("/opt/openclaw/openclaw.mjs agent")


def test_build_landlock_command_expands_runtime_segment_globs(tmp_path):
    site_packages = tmp_path / "site-packages"
    pip_dist_info = site_packages / "pip-24.3.1.dist-info"
    setuptools_dist_info = site_packages / "setuptools-70.0.0.dist-info"
    pip_dist_info.mkdir(parents=True)
    setuptools_dist_info.mkdir()
    (pip_dist_info / "METADATA").write_text("pip\n", encoding="utf-8")
    (setuptools_dist_info / "METADATA").write_text("setuptools\n", encoding="utf-8")

    command = build_landlock_command(
        permission_policy=normalize_permission_policy(
            {
                "read": [f"{site_packages}/pip-*.dist-info/**"],
                "write": [f"{site_packages}/pip-*.dist-info/**"],
                "execute": [],
            }
        ),
        implicit_permissions=normalize_permission_policy(
            {
                "read": [],
                "write": [],
                "execute": [],
            }
        ),
        command_argv=["/bin/true"],
    )

    argv = shlex.split(command)

    assert f"{pip_dist_info}/**" in argv
    assert f"{site_packages}/pip-*.dist-info/**" not in argv
    assert f"{setuptools_dist_info}/**" not in argv


def test_cli_openclaw_replay_sync(tmp_path, capsys):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-replay-cli"

    exit_code = main(
        [
            "openclaw-replay-task-sync",
            str(source),
            str(destination),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(destination.resolve()) in captured.out
    assert not (destination / "environment" / "authorization_policy.json").exists()


def test_cli_openclaw_replay_sync_accepts_task_local_timeout_overrides(tmp_path, capsys):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-replay-cli-timeout"

    exit_code = main(
        [
            "openclaw-replay-task-sync",
            str(source),
            str(destination),
            "--agent-timeout-sec",
            "900",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(destination.resolve()) in captured.out
    task_toml = (destination / "task.toml").read_text(encoding="utf-8")
    assert "[agent]\ntimeout_sec = 900.0" in task_toml
    openclaw_config = json.loads(
        (destination / "environment" / "openclaw_agent_config.json").read_text(
            encoding="utf-8"
        )
    )
    assert openclaw_config == {"timeout_sec": 900}


def test_cli_openclaw_replay_sync_with_policy_job(tmp_path, capsys, monkeypatch):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-replay-cli-job"
    artifact_path = (
        tmp_path
        / "jobs"
        / "permission-gen-hello-world-local"
        / "hello-world__trial123"
        / "artifacts"
        / "authorization_policy.json"
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(
        json.dumps({"read": [], "write": ["/app/hello.txt"], "execute": []}),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    exit_code = main(
        [
            "openclaw-replay-task-sync",
            str(source),
            str(destination),
            "--policy-job",
            "permission-gen-hello-world-local",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(destination.resolve()) in captured.out
    policy_json = (destination / "environment" / "authorization_policy.json").read_text(
        encoding="utf-8"
    )
    assert '"write": [' in policy_json


class _FakeExecResult:
    def __init__(self, return_code: int = 0, stdout: str | None = "", stderr: str | None = ""):
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr


class _FakeEnvironment:
    def __init__(self, files: dict[str, str]):
        self.files = dict(files)
        self.exec_calls: list[dict[str, object]] = []
        self.uploaded_files: dict[str, str] = {}
        self.uploaded_dirs: list[tuple[str, str]] = []

    async def exec(
        self,
        command: str,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout_sec: int | None = None,
    ) -> _FakeExecResult:
        self.exec_calls.append(
            {
                "command": command,
                "cwd": cwd,
                "env": dict(env) if env else None,
                "timeout_sec": timeout_sec,
            }
        )
        if command.startswith("test -f "):
            target = command.removeprefix("test -f ").strip().strip("'")
            return _FakeExecResult(return_code=0 if target in self.files else 1)
        if command.startswith("command -v "):
            return _FakeExecResult(return_code=0)
        if command.startswith("mkdir -p "):
            return _FakeExecResult(return_code=0)

        trajectory_path = "/tmp/openclaw-state-123456789abc/agents/authbench_task/sessions/authbench-123456789abc.jsonl"
        self.files[trajectory_path] = '{"type":"session_meta"}\n'
        return _FakeExecResult(return_code=0, stdout="agent ran", stderr="")

    async def upload_file(self, source_path: Path | str, target_path: str):
        self.uploaded_files[target_path] = Path(source_path).read_text(encoding="utf-8")

    async def upload_dir(self, source_dir: Path | str, target_dir: str):
        self.uploaded_dirs.append((str(source_dir), target_dir))

    async def download_file(self, source_path: str, target_path: Path | str):
        Path(target_path).write_text(self.files[source_path], encoding="utf-8")

    async def is_file(self, path: str) -> bool:
        return path in self.files


def test_openclaw_agent_runs_with_task_policy(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    policy_payload = json.dumps(
        {
            "read": ["/app/input.txt"],
            "write": ["/app/output.txt"],
            "execute": ["/usr/bin/python3"],
        }
    )
    eval_spec_payload = json.dumps(
        {
            "required_permissions": {
                "read": ["/app/input.txt"],
                "write": ["/app/output.txt"],
                "execute": ["/usr/bin/python3"],
            },
            "scored_roots": {
                "read": ["/app"],
                "write": ["/app"],
                "execute": ["/usr/bin"],
            },
            "implicit_permissions": {
                "read": ["/app/IDENTITY.md"],
                "write": ["/tmp/**"],
                "execute": ["/usr/local/bin/node"],
            },
        }
    )
    environment = _FakeEnvironment(
        {
            "/opt/authbench/authorization_policy.json": policy_payload,
            "/opt/authbench/permission_eval_spec.json": eval_spec_payload,
            "/opt/authbench/plugins/authbench-policy-guard/index.js": "module.exports = {};",
            LANDLOCK_LAUNCHER_PATH: "launcher",
        }
    )
    agent = OpenClawAgent(logs_dir=tmp_path, model_name="gpt-5-mini")

    import asyncio

    asyncio.run(agent.setup(environment))
    from harbor.models.agent.context import AgentContext

    context = AgentContext()
    monkeypatch.setattr(
        "libs.authbench_harbor_agents.openclaw_agent.uuid.uuid4",
        lambda: type("_UUID", (), {"hex": "123456789abc9999"})(),
    )
    asyncio.run(agent.run("Create hello.txt", environment, context))

    config_payload = json.loads(
        environment.uploaded_files["/tmp/openclaw-state-123456789abc/openclaw.json"]
    )
    plugin_config = config_payload["plugins"]["entries"]["authbench-policy-guard"]["config"]
    assert config_payload["agents"]["list"][0]["workspace"] == "/app"
    assert config_payload["skills"]["allowBundled"] == ["__authbench_no_bundled_skills__"]
    assert plugin_config == {
        "read": ["/app/input.txt", "/app/IDENTITY.md"],
        "write": ["/app/output.txt", "/tmp/**"],
        "execute": ["/usr/bin/python3", "/usr/local/bin/node"],
    }
    assert LANDLOCK_LAUNCHER_PATH in environment.exec_calls[-1]["command"]
    assert context.metadata is not None
    assert context.metadata["enforcement_mode"] == "policy"
    assert context.metadata["landlock_enabled"] is True
    assert context.metadata["return_code"] == 0
    assert context.metadata["timeout_sec"] == 900
    assert context.metadata["timeout_source"] == "default"
    assert context.metadata["implicit_permissions"] == {
        "read": ["/app/IDENTITY.md"],
        "write": ["/tmp/**"],
        "execute": ["/usr/local/bin/node"],
    }
    assert (tmp_path / "openclaw_stdout.log").read_text(encoding="utf-8") == "agent ran"


def test_openclaw_agent_uses_custom_provider_for_runtime_config(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.bltcy.ai/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    environment = _FakeEnvironment({})
    agent = OpenClawAgent(logs_dir=tmp_path, model_name="gpt-5")

    import asyncio

    asyncio.run(agent.setup(environment))
    from harbor.models.agent.context import AgentContext

    context = AgentContext()
    monkeypatch.setattr(
        "libs.authbench_harbor_agents.openclaw_agent.uuid.uuid4",
        lambda: type("_UUID", (), {"hex": "123456789abc9999"})(),
    )
    asyncio.run(agent.run("Create hello.txt", environment, context))

    config_payload = json.loads(
        environment.uploaded_files["/tmp/openclaw-state-123456789abc/openclaw.json"]
    )
    assert config_payload["agents"]["defaults"]["model"]["primary"] == "custom-api-bltcy-ai/gpt-5"
    assert "custom-api-bltcy-ai" in config_payload["models"]["providers"]
    assert "openai" not in config_payload["models"]["providers"]


def test_openclaw_agent_runs_allow_all_without_task_policy(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    environment = _FakeEnvironment({})
    agent = OpenClawAgent(logs_dir=tmp_path, model_name="gpt-5-mini")

    import asyncio

    asyncio.run(agent.setup(environment))
    from harbor.models.agent.context import AgentContext

    context = AgentContext()
    monkeypatch.setattr(
        "libs.authbench_harbor_agents.openclaw_agent.uuid.uuid4",
        lambda: type("_UUID", (), {"hex": "123456789abc9999"})(),
    )
    asyncio.run(agent.run("Create hello.txt", environment, context))

    config_payload = json.loads(
        environment.uploaded_files["/tmp/openclaw-state-123456789abc/openclaw.json"]
    )
    assert config_payload["plugins"] == {"enabled": False}
    assert set(config_payload["agents"]["list"][0]["tools"]["alsoAllow"]) == {
        "edit",
        "exec",
        "process",
        "read",
        "web_fetch",
        "web_search",
        "write",
    }
    assert LANDLOCK_LAUNCHER_PATH not in environment.exec_calls[-1]["command"]
    assert context.metadata is not None
    assert context.metadata["enforcement_mode"] == "allow_all"
    assert context.metadata["landlock_enabled"] is False
    assert context.metadata["return_code"] == 0


def test_openclaw_agent_uses_task_runtime_timeout_when_available(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    environment = _FakeEnvironment(
        {
            "/opt/authbench/openclaw_agent_config.json": json.dumps({"timeout_sec": 777}),
        }
    )
    agent = OpenClawAgent(logs_dir=tmp_path, model_name="gpt-5-mini")

    import asyncio

    asyncio.run(agent.setup(environment))
    from harbor.models.agent.context import AgentContext

    context = AgentContext()
    monkeypatch.setattr(
        "libs.authbench_harbor_agents.openclaw_agent.uuid.uuid4",
        lambda: type("_UUID", (), {"hex": "123456789abc9999"})(),
    )
    asyncio.run(agent.run("Create hello.txt", environment, context))

    assert "--timeout 777" in environment.exec_calls[-1]["command"]
    assert environment.exec_calls[-1]["timeout_sec"] == 777
    assert context.metadata is not None
    assert context.metadata["timeout_sec"] == 777
    assert context.metadata["timeout_source"] == "task_runtime_config"


def test_openclaw_agent_rejects_global_timeout_override_via_kwargs(tmp_path):
    try:
        OpenClawAgent(logs_dir=tmp_path, model_name="gpt-5-mini", timeout_sec=123)
    except ValueError as exc:
        assert "no longer accepts timeout overrides via agent kwargs" in str(exc)
    else:
        raise AssertionError("Expected timeout_sec kwarg to be rejected")
