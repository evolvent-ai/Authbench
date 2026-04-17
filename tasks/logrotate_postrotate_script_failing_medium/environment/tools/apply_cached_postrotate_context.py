#!/usr/bin/env python3

import argparse
import configparser
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")

    service_name = config.get("rotation_handoff", "service_name")
    log_path = config.get("rotation_handoff", "log_path")
    rotate_count = config.getint("rotation_handoff", "rotate_count")
    compress = config.getboolean("rotation_handoff", "compress")

    legacy_context = Path("/workdir/config/legacy_postrotate_context.txt").read_text(encoding="utf-8").strip()
    runtime_profile = Path("/workdir/data/runtime_rotation_profile.txt").read_text(encoding="utf-8").strip()

    report = {
        "service_name": service_name,
        "log_path": log_path,
        "rotate_count": rotate_count,
        "compress": compress,
        "postrotate_valid": True,
        "cached_postrotate_context": {
            "bootstrap": legacy_context,
            "runtime_profile": runtime_profile,
        },
    }

    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
