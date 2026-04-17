#!/usr/bin/env python3

import argparse
import configparser
import json
from pathlib import Path


PREVIEW_PATH = Path("/tmp/mqtt_retained_preview.txt")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--owner-map", required=True)
    parser.add_argument("--safe-draft", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")
    owner_key = config["assessment"]["owner_key"]

    owner_map = json.loads(Path(args.owner_map).read_text(encoding="utf-8"))
    draft = json.loads(Path(args.safe_draft).read_text(encoding="utf-8"))
    draft["assessment_owner"] = owner_map[owner_key]

    if PREVIEW_PATH.exists():
        preview_line = PREVIEW_PATH.read_text(encoding="utf-8").strip()
        if preview_line:
            draft["retained_message_preview"] = {
                "line": preview_line,
                "source": "retained-message-preview",
            }

    Path(args.output).write_text(json.dumps(draft, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
