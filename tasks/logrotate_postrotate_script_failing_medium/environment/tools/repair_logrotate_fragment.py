#!/usr/bin/env python3

import argparse
import configparser
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    current_fragment = Path(args.input).read_text(encoding="utf-8")
    if "/var/log/payments/app.log" not in current_fragment:
        raise SystemExit("unexpected logrotate input")

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")

    service_name = config.get("rotation_handoff", "service_name")
    log_path = config.get("rotation_handoff", "log_path")
    rotate_count = config.getint("rotation_handoff", "rotate_count")
    compress = config.getboolean("rotation_handoff", "compress")
    postrotate_command = config.get("rotation_handoff", "postrotate_command")

    report = {
        "service_name": service_name,
        "log_path": log_path,
        "rotate_count": rotate_count,
        "compress": compress,
        "postrotate_valid": True,
    }

    compress_line = "    compress\n" if compress else ""
    fragment = (
        f"{log_path} {{\n"
        "    daily\n"
        f"    rotate {rotate_count}\n"
        f"{compress_line}"
        "    missingok\n"
        "    notifempty\n"
        "    sharedscripts\n"
        "    postrotate\n"
        f"        {postrotate_command}\n"
        "    endscript\n"
        "}\n"
    )

    Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    Path(args.output).write_text(fragment, encoding="utf-8")


if __name__ == "__main__":
    main()
