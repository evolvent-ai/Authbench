from __future__ import annotations

import json
import math
import os
import shlex
import uuid
from pathlib import Path

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

from libs.authbench_sync.file_rwx import (
    PermissionPolicy,
    load_permission_eval_spec_file,
    permission_policy_to_payload,
)
from libs.openclaw_replay_assets.openclaw_verifier_shared.openclaw_verifier_lib.constants import (
    DEFAULT_AGENT_ID,
    DEFAULT_MODEL,
    OPENCLAW_WORKSPACE_PATH,
    POLICY_PATH,
)
from libs.openclaw_replay_assets.openclaw_verifier_shared.openclaw_verifier_lib.policy import (
    load_policy,
)
from libs.openclaw_replay_assets.openclaw_verifier_shared.openclaw_verifier_lib.policy_enforcement import (
    LANDLOCK_LAUNCHER_PATH,
    POLICY_GUARD_PLUGIN_ID,
    build_landlock_command,
    write_exec_approvals,
)
from libs.openclaw_replay_assets.openclaw_verifier_shared.openclaw_verifier_lib.runtime import (
    build_config,
)

_REMOTE_PLUGIN_DIR = Path("/opt/authbench/plugins") / POLICY_GUARD_PLUGIN_ID
_REMOTE_EVAL_SPEC_PATH = Path("/opt/authbench/permission_eval_spec.json")
_REMOTE_AGENT_CONFIG_PATH = Path("/opt/authbench/openclaw_agent_config.json")
_ALLOW_ALL_TOOLS = ("edit", "exec", "process", "read", "web_fetch", "web_search", "write")
_NO_BUNDLED_SKILLS_ALLOWLIST = ["__authbench_no_bundled_skills__"]
_REQUIRED_ENV_KEYS = ("OPENAI_BASE_URL", "OPENAI_API_KEY")
_DEFAULT_TIMEOUT_SEC = 900


class OpenClawAgent(BaseAgent):
    def __init__(
        self,
        logs_dir: Path,
        model_name: str | None = None,
        agent_id: str = DEFAULT_AGENT_ID,
        extra_env: dict[str, str] | None = None,
        *args,
        **kwargs,
    ):
        if "timeout_sec" in kwargs:
            raise ValueError(
                "OpenClawAgent no longer accepts timeout overrides via agent kwargs; "
                "set the replay task's [agent].timeout_sec instead."
            )
        resolved_model_name = model_name or DEFAULT_MODEL
        super().__init__(logs_dir, resolved_model_name, *args, **kwargs)
        self._agent_id = agent_id.strip() or DEFAULT_AGENT_ID
        self._extra_env = dict(extra_env) if extra_env else {}

    @staticmethod
    def name() -> str:
        return "openclaw"

    def version(self) -> str:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        checks = [
            ("openclaw binary", "command -v openclaw >/dev/null"),
            ("node binary", "command -v node >/dev/null"),
        ]
        for label, command in checks:
            result = await environment.exec(command=command, timeout_sec=15)
            if result.return_code != 0:
                raise RuntimeError(f"OpenClaw agent setup check failed: missing {label}")

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        agent_env = self._resolve_agent_env()
        run_id = uuid.uuid4().hex[:12]
        session_id = f"authbench-{run_id}"
        local_home_dir = self.logs_dir / "openclaw-home"
        local_state_dir = self.logs_dir / "openclaw-state"
        local_policy_path = self.logs_dir / "authorization_policy.json"
        local_eval_spec_path = self.logs_dir / "permission_eval_spec.json"
        local_config_path = local_state_dir / "openclaw.json"
        local_stdout_path = self.logs_dir / "openclaw_stdout.log"
        local_stderr_path = self.logs_dir / "openclaw_stderr.log"
        local_summary_path = self.logs_dir / "openclaw_agent_summary.json"
        local_runtime_config_path = self.logs_dir / "openclaw_agent_config.json"
        local_home_dir.mkdir(parents=True, exist_ok=True)
        local_state_dir.mkdir(parents=True, exist_ok=True)
        timeout_sec, timeout_source = await self._resolve_timeout_sec(
            environment=environment,
            local_runtime_config_path=local_runtime_config_path,
        )

        loaded_policy = None
        permission_policy = None
        implicit_permissions = PermissionPolicy(read=(), write=(), execute=())
        if await environment.is_file(str(POLICY_PATH)):
            if not await environment.is_file(str(_REMOTE_PLUGIN_DIR / "index.js")):
                raise RuntimeError("OpenClaw agent setup check failed: missing policy guard plugin")
            if not await environment.is_file(LANDLOCK_LAUNCHER_PATH):
                raise RuntimeError("OpenClaw agent setup check failed: missing Landlock launcher")
            if not await environment.is_file(str(_REMOTE_EVAL_SPEC_PATH)):
                raise RuntimeError("OpenClaw agent setup check failed: missing permission eval spec")
            await environment.download_file(str(POLICY_PATH), local_policy_path)
            await environment.download_file(str(_REMOTE_EVAL_SPEC_PATH), local_eval_spec_path)
            loaded_policy, policy_meta = load_policy(local_policy_path)
            if loaded_policy is None:
                raise ValueError(f"Invalid OpenClaw policy: {policy_meta}")
            eval_spec = load_permission_eval_spec_file(local_eval_spec_path)
            permission_policy = loaded_policy.normalized_policy
            implicit_permissions = eval_spec.implicit_permissions
            allowed_tools = loaded_policy.mapped_tools
            execute_permissions: list[str] | tuple[str, ...] = loaded_policy.permission_policy.execute
            plugin_dir = _REMOTE_PLUGIN_DIR
            plugin_id = POLICY_GUARD_PLUGIN_ID
            plugin_config = permission_policy_to_payload(
                _merge_permission_policies(
                    loaded_policy.permission_policy,
                    implicit_permissions,
                )
            )
            enforcement_mode = "policy"
        else:
            policy_meta = {"policy_found": False, "mode": "allow_all"}
            allowed_tools = list(_ALLOW_ALL_TOOLS)
            execute_permissions = ["*"]
            plugin_dir = None
            plugin_id = None
            plugin_config = None
            enforcement_mode = "allow_all"

        if execute_permissions:
            exec_allowlist_meta = write_exec_approvals(
                home_dir=local_home_dir,
                agent_id=self._agent_id,
                execute_permissions=execute_permissions,
            )
        else:
            exec_allowlist_meta = {
                "exec_allowlist_path": None,
                "exec_allowlist_patterns": [],
                "exec_allowlist_count": 0,
                "reason": "execute_not_enabled",
            }

        config_payload = build_config(
            agent_id=self._agent_id,
            model_id=self.model_name or DEFAULT_MODEL,
            allowed_tools=allowed_tools,
            workspace_path=OPENCLAW_WORKSPACE_PATH,
            policy_guard_plugin_dir=plugin_dir,
            policy_guard_plugin_id=plugin_id,
            policy_guard_plugin_config=plugin_config,
            allow_bundled_skills=_NO_BUNDLED_SKILLS_ALLOWLIST,
            base_url=agent_env.get("OPENAI_BASE_URL"),
        )
        local_config_path.write_text(
            json.dumps(config_payload, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )

        remote_state_dir = f"/tmp/openclaw-state-{run_id}"
        remote_home_dir = f"/tmp/openclaw-home-{run_id}"
        remote_config_path = f"{remote_state_dir}/openclaw.json"
        await environment.exec(
            command=(
                f"mkdir -p {shlex.quote(remote_state_dir)} "
                f"{shlex.quote(remote_home_dir)}"
            ),
            timeout_sec=15,
        )
        await environment.upload_file(local_config_path, remote_config_path)
        if (local_home_dir / ".openclaw").exists():
            await environment.upload_dir(local_home_dir, remote_home_dir)

        openclaw_env = dict(agent_env)
        openclaw_env["OPENCLAW_STATE_DIR"] = remote_state_dir
        openclaw_env["HOME"] = remote_home_dir
        if plugin_config is not None:
            openclaw_env["AUTHBENCH_POLICY_PROJECT_ROOT"] = str(OPENCLAW_WORKSPACE_PATH)

        openclaw_argv = [
            "/usr/local/bin/node",
            "/opt/openclaw/openclaw.mjs",
            "agent",
            "--local",
            "--agent",
            self._agent_id,
            "--session-id",
            session_id,
            "--message",
            instruction,
            "--timeout",
            str(timeout_sec),
            "--json",
        ]
        if loaded_policy is not None:
            command = build_landlock_command(
                permission_policy=loaded_policy.permission_policy,
                implicit_permissions=implicit_permissions,
                command_argv=openclaw_argv,
            )
        else:
            command = " ".join(shlex.quote(arg) for arg in openclaw_argv)

        result = await environment.exec(
            command=command,
            cwd=str(OPENCLAW_WORKSPACE_PATH),
            env=openclaw_env,
            timeout_sec=timeout_sec,
        )

        local_stdout_path.write_text(result.stdout or "", encoding="utf-8")
        local_stderr_path.write_text(result.stderr or "", encoding="utf-8")

        remote_trajectory_path = (
            f"{remote_state_dir}/agents/{self._agent_id}/sessions/{session_id}.jsonl"
        )
        local_trajectory_path = self.logs_dir / "openclaw_trajectory.jsonl"
        if await environment.is_file(remote_trajectory_path):
            await environment.download_file(remote_trajectory_path, local_trajectory_path)

        summary = {
            "status": "ok" if result.return_code == 0 else "failed",
            "agent_id": self._agent_id,
            "session_id": session_id,
            "model": self.model_name or DEFAULT_MODEL,
            "return_code": result.return_code,
            "remote_state_dir": remote_state_dir,
            "remote_home_dir": remote_home_dir,
            "workspace_path": str(OPENCLAW_WORKSPACE_PATH),
            "timeout_sec": timeout_sec,
            "timeout_source": timeout_source,
            "enforcement_mode": enforcement_mode,
            "landlock_enabled": loaded_policy is not None,
            "policy_meta": policy_meta,
            "permission_policy": permission_policy,
            "implicit_permissions": permission_policy_to_payload(implicit_permissions),
            "exec_allowlist_meta": exec_allowlist_meta,
            "trajectory_path": str(local_trajectory_path)
            if local_trajectory_path.exists()
            else None,
        }
        local_summary_path.write_text(
            json.dumps(summary, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        context.metadata = summary

    async def _resolve_timeout_sec(
        self,
        *,
        environment: BaseEnvironment,
        local_runtime_config_path: Path,
    ) -> tuple[int, str]:
        if await environment.is_file(str(_REMOTE_AGENT_CONFIG_PATH)):
            await environment.download_file(
                str(_REMOTE_AGENT_CONFIG_PATH),
                local_runtime_config_path,
            )
            return (
                _load_runtime_timeout_sec(local_runtime_config_path),
                "task_runtime_config",
            )

        return _DEFAULT_TIMEOUT_SEC, "default"

    def _resolve_agent_env(self) -> dict[str, str]:
        resolved = {
            key: value
            for key in _REQUIRED_ENV_KEYS
            if (value := os.environ.get(key))
        }
        resolved.update(self._extra_env)
        missing = [key for key in _REQUIRED_ENV_KEYS if not resolved.get(key)]
        if missing:
            joined = ", ".join(missing)
            raise ValueError(
                f"OpenClaw agent requires environment variables: {joined}"
            )
        return resolved


def _merge_permission_policies(
    left: PermissionPolicy,
    right: PermissionPolicy,
) -> PermissionPolicy:
    return PermissionPolicy(
        read=_dedupe(left.read, right.read),
        write=_dedupe(left.write, right.write),
        execute=_dedupe(left.execute, right.execute),
    )


def _dedupe(*groups: tuple[str, ...]) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group:
            if item in seen:
                continue
            seen.add(item)
            ordered.append(item)
    return tuple(ordered)


def _load_runtime_timeout_sec(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"OpenClaw runtime config must be an object: {path}")
    if "timeout_sec" not in payload:
        raise ValueError(f"OpenClaw runtime config missing timeout_sec: {path}")
    return _coerce_positive_timeout_sec(
        payload["timeout_sec"],
        label="OpenClaw runtime timeout",
    )


def _coerce_positive_timeout_sec(value: object, *, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")

    try:
        timeout_sec = math.ceil(float(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc

    if timeout_sec <= 0:
        raise ValueError(f"{label} must be > 0 seconds")
    return int(timeout_sec)
