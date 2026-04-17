from __future__ import annotations

from pathlib import Path

APP_DIR = Path("/app")
AUTHBENCH_DIR = Path("/opt/authbench")
POLICY_PATH = AUTHBENCH_DIR / "authorization_policy.json"
OPENCLAW_WORKSPACE_PATH = APP_DIR

DEFAULT_AGENT_ID = "authbench_task"
DEFAULT_MODEL = "gpt-5-mini"
