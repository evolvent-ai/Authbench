#!/bin/bash
set -euo pipefail

/usr/local/bin/python3 - <<'PY'
from pathlib import Path

agent_source = """from __future__ import annotations

import json
from pathlib import Path


class Agent:
    def __init__(self) -> None:
        self.weights = [0.05, 0.01, 1.0, 0.5]
        self.bias = 0.0

    def _score(self, current_observation) -> float:
        x, x_dot, theta, theta_dot = current_observation
        return (
            self.weights[0] * x
            + self.weights[1] * x_dot
            + self.weights[2] * theta
            + self.weights[3] * theta_dot
            + self.bias
        )

    def select_action(self, current_observation):
        return 1 if self._score(current_observation) >= 0 else 0

    def save(self, dir_path):
        target = Path(dir_path)
        target.mkdir(parents=True, exist_ok=True)
        payload = {"weights": self.weights, "bias": self.bias}
        (target / "policy.json").write_text(json.dumps(payload))

    def load(self, dir_path):
        target = Path(dir_path) / "policy.json"
        payload = json.loads(target.read_text())
        self.weights = [float(value) for value in payload["weights"]]
        self.bias = float(payload["bias"])
"""

Path("/app/agent.py").write_text(agent_source)
PY

/usr/local/bin/python3 - <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, "/app")

from agent import Agent

agent = Agent()
agent.save("/app/trained_model")
agent.load("/app/trained_model")

if not Path("/app/trained_model/policy.json").is_file():
    raise SystemExit("policy file was not created")
PY
