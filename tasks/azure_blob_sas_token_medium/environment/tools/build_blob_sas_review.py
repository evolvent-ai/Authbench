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

    storage_account = section["storage_account"]
    container = section["container"]
    blob_prefix = section["blob_prefix"]

    assert storage_account in request_text, "request missing storage account"
    assert container in request_text, "request missing container"
    assert inventory["storage_account"] == storage_account, "inventory storage account mismatch"
    assert inventory["container"] == container, "inventory container mismatch"
    assert inventory["blob_prefix"] == blob_prefix, "inventory blob prefix mismatch"

    report = {
        "storage_account": storage_account,
        "container": container,
        "blob_prefix": blob_prefix,
        "finding": section["finding"],
        "risk_level": section["risk_level"],
        "review_ticket": section["review_ticket"],
        "recommended_action": section["recommended_action"],
        "next_step": section["next_step"],
    }
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
