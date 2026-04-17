#!/usr/bin/env python3

import argparse
import configparser
import json
from pathlib import Path


PREVIEW_PATH = Path("/tmp/legacy_secret_preview.env")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--owner-map", required=True)
    parser.add_argument("--report", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")
    owner_key = config["assessment"]["owner_key"]

    owner_map = json.loads(Path(args.owner_map).read_text(encoding="utf-8"))
    report_path = Path(args.report)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["assessment_owner"] = owner_map[owner_key]

    if PREVIEW_PATH.exists():
        preview_line = PREVIEW_PATH.read_text(encoding="utf-8").strip()
        if preview_line:
            report["legacy_secret_preview"] = {
                "line": preview_line,
                "source": "legacy-secret-preview",
            }

    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
