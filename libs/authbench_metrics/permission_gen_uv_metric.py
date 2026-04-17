from __future__ import annotations

import argparse
from pathlib import Path

if __package__ in {None, ""}:
    from replay_metric_common import (  # type: ignore[import-not-found]
        load_jsonl_values,
        mean,
        parse_metric_args,
        write_metrics_output,
    )
else:
    from .replay_metric_common import (
        load_jsonl_values,
        mean,
        parse_metric_args,
        write_metrics_output,
    )

DEFAULT_KEYS = (
    "reward",
    "step_total",
    "read_precision",
    "read_recall",
    "read_f1",
    "write_precision",
    "write_recall",
    "write_f1",
    "execute_precision",
    "execute_recall",
    "execute_f1",
)
SENSITIVE_KEY = "sensitive_exposure_coverage"


def _normalize_reward(payload: object) -> dict[str, float | int]:
    if payload is None or not isinstance(payload, dict):
        return {}
    numeric_payload: dict[str, float | int] = {}
    for key, value in payload.items():
        if isinstance(value, bool):
            numeric_payload[key] = int(value)
        elif isinstance(value, (int, float)):
            numeric_payload[key] = value
    return numeric_payload


def _load_rewards(path: Path) -> list[dict[str, float | int]]:
    return load_jsonl_values(path, normalize=_normalize_reward)


def _mean_key(rewards: list[dict[str, float | int]], key: str) -> float:
    return mean([reward.get(key, 0) for reward in rewards])


def compute_metrics(rewards: list[dict[str, float | int]]) -> dict[str, float | int]:
    sensitive_values = [reward[SENSITIVE_KEY] for reward in rewards if SENSITIVE_KEY in reward]
    output: dict[str, float | int] = {
        "n_trials": len(rewards),
        "n_sensitive_trials": len(sensitive_values),
        "success_rate": _mean_key(rewards, "reward"),
    }
    for key in DEFAULT_KEYS:
        output[f"{key}_mean"] = _mean_key(rewards, key)
    output[f"{SENSITIVE_KEY}_mean"] = mean(sensitive_values)
    return output


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return parse_metric_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    rewards = _load_rewards(args.input)
    metrics = compute_metrics(rewards)
    write_metrics_output(args.output, metrics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
