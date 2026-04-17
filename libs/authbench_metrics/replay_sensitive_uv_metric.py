from __future__ import annotations

import argparse
from pathlib import Path

if __package__ in {None, ""}:
    from replay_metric_common import (  # type: ignore[import-not-found]
        load_normalized_rewards,
        mean,
        parse_metric_args,
        require_numeric_flag,
        write_metrics_output,
    )
else:
    from .replay_metric_common import (
        load_normalized_rewards,
        mean,
        parse_metric_args,
        require_numeric_flag,
        write_metrics_output,
    )


def _normalize_reward(payload: object) -> dict[str, int]:
    if payload is None:
        return {
            "reward": 0,
            "utility_success": 0,
            "attack_success": 0,
            "is_safety_only": 0,
        }
    if not isinstance(payload, dict):
        raise ValueError(f"Expected reward mapping or null, got: {type(payload).__name__}")
    return {
        "reward": require_numeric_flag(payload, "reward"),
        "utility_success": require_numeric_flag(payload, "utility_success"),
        "attack_success": require_numeric_flag(payload, "attack_success"),
        "is_safety_only": require_numeric_flag(payload, "is_safety_only"),
    }


def _load_rewards(path: Path) -> list[dict[str, int]]:
    return load_normalized_rewards(path, normalize=_normalize_reward)


def compute_metrics(rewards: list[dict[str, int]]) -> dict[str, float | int]:
    return {
        "n_trials": len(rewards),
        "success_rate": mean([reward["reward"] for reward in rewards]),
        "utility_success_rate": mean(
            [reward["utility_success"] for reward in rewards]
        ),
        "attack_success_rate": mean(
            [reward["attack_success"] for reward in rewards]
        ),
        "n_safety_only_trials": sum(
            reward["is_safety_only"] for reward in rewards
        ),
        "n_mixed_trials": sum(1 - reward["is_safety_only"] for reward in rewards),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return parse_metric_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    metrics = compute_metrics(_load_rewards(args.input))
    write_metrics_output(args.output, metrics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
