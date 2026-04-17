from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from libs.authbench_metrics.replay_sensitive_uv_metric import (
    compute_metrics as compute_sensitive_metrics,
)
from libs.authbench_metrics.replay_standard_uv_metric import (
    compute_metrics as compute_standard_metrics,
)


def test_replay_standard_uv_metric_computes_success_and_utility_rates() -> None:
    metrics = compute_standard_metrics(
        [
            {"reward": 1, "utility_success": 1},
            {"reward": 0, "utility_success": 0},
            {"reward": 1, "utility_success": 1},
        ]
    )

    assert metrics == {
        "n_trials": 3,
        "success_rate": 2 / 3,
        "utility_success_rate": 2 / 3,
    }


def test_replay_sensitive_uv_metric_counts_attack_and_safety_only_trials() -> None:
    metrics = compute_sensitive_metrics(
        [
            {
                "reward": 1,
                "utility_success": 1,
                "attack_success": 0,
                "is_safety_only": 0,
            },
            {
                "reward": 0,
                "utility_success": 0,
                "attack_success": 1,
                "is_safety_only": 1,
            },
        ]
    )

    assert metrics == {
        "n_trials": 2,
        "success_rate": 0.5,
        "utility_success_rate": 0.5,
        "attack_success_rate": 0.5,
        "n_safety_only_trials": 1,
        "n_mixed_trials": 1,
    }


def test_replay_standard_metric_script_runs_as_standalone_file(tmp_path: Path) -> None:
    input_path = tmp_path / "rewards.jsonl"
    output_path = tmp_path / "metrics.json"
    input_path.write_text(
        json.dumps({"reward": 1, "utility_success": 1}) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(Path("libs/authbench_metrics/replay_standard_uv_metric.py").resolve()),
            "-i",
            str(input_path),
            "-o",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["n_trials"] == 1
    assert payload["success_rate"] == 1.0
