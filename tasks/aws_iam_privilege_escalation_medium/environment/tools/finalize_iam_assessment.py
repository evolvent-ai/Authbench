#!/usr/bin/env python3

import argparse
import configparser
import json
from pathlib import Path


QUEUE_MAP_PATH = Path("/workdir/data/assessment_queue_map.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--report", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")
    queue_key = config["assessment"]["queue_key"]

    queue_map = json.loads(QUEUE_MAP_PATH.read_text(encoding="utf-8"))
    report_path = Path(args.report)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["assessment_queue"] = queue_map[queue_key]
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
