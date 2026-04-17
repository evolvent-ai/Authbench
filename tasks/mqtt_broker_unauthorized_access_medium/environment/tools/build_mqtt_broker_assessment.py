#!/usr/bin/env python3

import argparse
import configparser
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request_text = Path(args.request).read_text(encoding="utf-8")
    inventory = json.loads(Path(args.inventory).read_text(encoding="utf-8"))

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")
    section = config["assessment"]

    broker_id = section["broker_id"]
    listener = section["listener"]
    topic_prefix = section["topic_prefix"]

    assert broker_id in request_text, "request missing broker id"
    assert listener in request_text, "request missing listener"
    assert inventory["broker_id"] == broker_id, "inventory broker mismatch"
    assert inventory["listener"] == listener, "inventory listener mismatch"
    assert inventory["topic_prefix"] == topic_prefix, "inventory topic mismatch"

    report = {
        "broker_id": broker_id,
        "listener": listener,
        "topic_prefix": topic_prefix,
        "review_mode": section["review_mode"],
        "risk_level": section["risk_level"],
        "recommended_action": section["recommended_action"],
        "next_step": section["next_step"],
    }
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
