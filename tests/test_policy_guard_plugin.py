from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

PLUGIN_PATH = (
    Path("libs/openclaw_replay_assets/openclaw_plugins/authbench-policy-guard/index.js")
    .resolve()
)


def _run_plugin(plugin_config: dict[str, object], event: dict[str, object]) -> object:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is required for plugin tests")

    script = f"""
const plugin = require({json.dumps(str(PLUGIN_PATH))});
let handler = null;
plugin.register({{
  pluginConfig: {json.dumps(plugin_config)},
  on(name, fn) {{
    if (name === "before_tool_call") {{
      handler = fn;
    }}
  }},
}});
if (!handler) {{
  throw new Error("before_tool_call handler not registered");
}}
(async () => {{
  const result = await handler({json.dumps(event)});
  process.stdout.write(JSON.stringify(result ?? null));
}})().catch((err) => {{
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
}});
"""
    env = os.environ.copy()
    env["AUTHBENCH_POLICY_PROJECT_ROOT"] = "/app"
    proc = subprocess.run(
        [node, "-e", script],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return json.loads(proc.stdout or "null")


def test_policy_guard_read_enforces_allowed_paths():
    plugin_config = {
        "read": ["/app/input.txt"],
        "write": [],
        "execute": [],
    }

    allowed = _run_plugin(
        plugin_config,
        {
            "toolName": "read",
            "params": {"path": "/app/input.txt"},
        },
    )
    denied = _run_plugin(
        plugin_config,
        {
            "toolName": "read",
            "params": {"path": "/app/other.txt"},
        },
    )

    assert allowed is None
    assert denied["block"] is True
    assert "/app/other.txt" in denied["blockReason"]


def test_policy_guard_write_accepts_file_path_alias():
    plugin_config = {
        "read": [],
        "write": ["/app/output.txt"],
        "execute": [],
    }

    allowed = _run_plugin(
        plugin_config,
        {
            "toolName": "write",
            "params": {"file_path": "/app/output.txt", "content": "hello"},
        },
    )
    denied = _run_plugin(
        plugin_config,
        {
            "toolName": "write",
            "params": {"file_path": "/app/other.txt", "content": "hello"},
        },
    )

    assert allowed is None
    assert denied["block"] is True
    assert "/app/other.txt" in denied["blockReason"]


def test_policy_guard_write_resolves_relative_path_against_global_workspace_path():
    plugin_config = {
        "read": [],
        "write": ["/app/output.txt"],
        "execute": [],
    }

    allowed = _run_plugin(
        plugin_config,
        {
            "toolName": "write",
            "params": {"file_path": "output.txt", "content": "hello"},
        },
    )
    denied = _run_plugin(
        plugin_config,
        {
            "toolName": "write",
            "params": {"file_path": "../etc/passwd", "content": "hello"},
        },
    )

    assert allowed is None
    assert denied["block"] is True
    assert "/etc/passwd" in denied["blockReason"]
