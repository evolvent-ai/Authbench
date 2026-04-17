from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from libs.authbench_metrics.permission_gen_uv_metric import compute_metrics


def test_compute_metrics_aggregates_expected_fields():
    rewards = [
        {
            'reward': 1,
            'step_total': 6,
            'read_precision': 0.5,
            'read_recall': 1.0,
            'read_f1': 2 / 3,
            'write_precision': 1.0,
            'write_recall': 1.0,
            'write_f1': 1.0,
            'execute_precision': 0.25,
            'execute_recall': 0.5,
            'execute_f1': 1 / 3,
            'sensitive_exposure_coverage': 0.25,
        },
        {
            'reward': 0,
            'step_total': 4,
            'read_precision': 0.0,
            'read_recall': 0.0,
            'read_f1': 0.0,
            'write_precision': 0.0,
            'write_recall': 0.0,
            'write_f1': 0.0,
            'execute_precision': 0.0,
            'execute_recall': 0.0,
            'execute_f1': 0.0,
        },
    ]

    result = compute_metrics(rewards)

    assert result['n_trials'] == 2
    assert result['n_sensitive_trials'] == 1
    assert result['success_rate'] == 0.5
    assert result['reward_mean'] == 0.5
    assert result['step_total_mean'] == 5.0
    assert result['read_precision_mean'] == 0.25
    assert result['read_recall_mean'] == 0.5
    assert round(result['read_f1_mean'], 6) == round((2 / 3) / 2, 6)
    assert result['write_precision_mean'] == 0.5
    assert result['write_recall_mean'] == 0.5
    assert result['write_f1_mean'] == 0.5
    assert result['execute_precision_mean'] == 0.125
    assert result['execute_recall_mean'] == 0.25
    assert round(result['execute_f1_mean'], 6) == round((1 / 3) / 2, 6)
    assert result['sensitive_exposure_coverage_mean'] == 0.25


def test_permission_gen_metric_script_runs_as_standalone_file(tmp_path: Path) -> None:
    input_path = tmp_path / "rewards.jsonl"
    output_path = tmp_path / "metrics.json"
    input_path.write_text(
        json.dumps({"reward": 1, "step_total": 2}) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(Path("libs/authbench_metrics/permission_gen_uv_metric.py").resolve()),
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
