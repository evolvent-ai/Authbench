from __future__ import annotations

import json
from pathlib import Path

from harbor.agents.terminus_2 import Terminus2
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

from libs.authbench_sync.common import POLICY_OUTPUT_PATH
from libs.authbench_sync.file_rwx import load_permission_policy_file

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
_SUFFICIENCY_PROMPT_PATH = _PROMPTS_DIR / "st_sufficiency_terminus_json_prompt_en.txt"
_TIGHTNESS_PROMPT_PATH = _PROMPTS_DIR / "st_tightness_terminus_json_prompt_en.txt"
_SUFFICIENCY_POLICY_PATH = "/app/.authbench_sufficiency_policy.json"


class _STPermissionAgent(Terminus2):
    """Terminus2 profile for phase-specific AuthBench permission generation."""

    _phase_name = "unknown"
    _prompt_path = _SUFFICIENCY_PROMPT_PATH

    def _get_prompt_template_path(self) -> Path:
        if getattr(self, "_parser_name", "json") != "json":
            raise ValueError(f"{self.__class__.__name__} currently supports parser_name='json' only")
        return self._prompt_path

    def _get_completion_confirmation_message(self, terminal_output: str) -> str:
        return (
            f"Current terminal state:\n{terminal_output}\n\n"
            "Are you sure the authorization policy is complete? "
            "This will trigger grading and you will not be able to make further corrections. "
            'If so, include "task_complete": true in your JSON response again.'
        )

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        try:
            await super().run(instruction, environment, context)
        finally:
            await self._write_run_summary(environment, context)

    async def _write_run_summary(self, environment: BaseEnvironment, context: AgentContext) -> None:
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        local_policy_path = self.logs_dir / "authorization_policy.json"
        summary_path = self.logs_dir / "st_decomposition_agent_summary.json"
        summary: dict[str, object] = {
            "agent": self.name(),
            "version": self.version(),
            "phase": self._phase_name,
            "prompt_template": str(self._prompt_path),
            "policy_found": False,
            "policy_valid": False,
        }

        if await environment.is_file(POLICY_OUTPUT_PATH):
            summary["policy_found"] = True
            await environment.download_file(POLICY_OUTPUT_PATH, local_policy_path)
            try:
                policy = load_permission_policy_file(local_policy_path)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                summary["policy_error"] = str(exc)
            else:
                summary["policy_valid"] = True
                summary["policy_counts"] = {
                    "read": len(policy.read),
                    "write": len(policy.write),
                    "execute": len(policy.execute),
                }

        context.metadata = dict(context.metadata or {})
        context.metadata["st_decomposition_agent"] = {
            "phase": self._phase_name,
            "summary_path": str(summary_path),
        }
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )


class AuthSufficiencyAgent(_STPermissionAgent):
    """Phase 1 agent that generates a coverage-oriented policy candidate."""

    _phase_name = "sufficiency"
    _prompt_path = _SUFFICIENCY_PROMPT_PATH

    @staticmethod
    def name() -> str:
        return "auth-sufficiency"

    def version(self) -> str | None:
        return "0.1.0"


class AuthTightnessAgent(_STPermissionAgent):
    """Phase 2 agent that tightens a mounted sufficiency policy."""

    _phase_name = "tightness"
    _prompt_path = _TIGHTNESS_PROMPT_PATH

    @staticmethod
    def name() -> str:
        return "auth-tightness"

    def version(self) -> str | None:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        if not await environment.is_file(_SUFFICIENCY_POLICY_PATH):
            raise RuntimeError(f"AuthTightnessAgent requires {_SUFFICIENCY_POLICY_PATH}")
        await super().setup(environment)
