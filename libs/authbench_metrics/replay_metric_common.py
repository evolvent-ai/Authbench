from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path


def mean(values: list[int | float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def require_numeric_flag(payload: dict[str, object], key: str) -> int:
    if key not in payload:
        raise ValueError(f"Missing reward key: {key}")
    value = payload[key]
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    raise ValueError(f"Reward key {key!r} must be numeric")


def parse_metric_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    return parser.parse_args(argv)


def write_metrics_output(path: Path, metrics: object) -> None:
    path.write_text(
        json.dumps(metrics, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )


def load_jsonl_values[T](
    path: Path,
    *,
    normalize: Callable[[object], T],
) -> list[T]:
    values: list[T] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        values.append(normalize(json.loads(line)))
    return values


def load_normalized_rewards(
    path: Path,
    *,
    normalize: Callable[[object], dict[str, int]],
) -> list[dict[str, int]]:
    return load_jsonl_values(path, normalize=normalize)
