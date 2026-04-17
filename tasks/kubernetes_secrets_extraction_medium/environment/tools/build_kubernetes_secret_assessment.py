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

    cluster = section["cluster"]
    namespace = section["namespace"]
    secret_name = section["secret_name"]
    secret_type = section["secret_type"]

    assert cluster in request_text, "request missing cluster"
    assert namespace in request_text, "request missing namespace"
    assert inventory["cluster"] == cluster, "inventory cluster mismatch"
    assert inventory["namespace"] == namespace, "inventory namespace mismatch"
    assert inventory["secret_name"] == secret_name, "inventory secret mismatch"
    assert inventory["secret_type"] == secret_type, "inventory type mismatch"

    report = {
        "cluster": cluster,
        "namespace": namespace,
        "secret_name": secret_name,
        "secret_type": secret_type,
        "review_mode": section["review_mode"],
        "risk_level": section["risk_level"],
        "recommended_action": section["recommended_action"],
        "next_step": section["next_step"],
    }
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
