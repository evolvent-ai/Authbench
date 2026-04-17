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

    current_template = json.loads(Path(args.input).read_text(encoding="utf-8"))

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")

    webhook_url = config.get("pagerduty_delivery", "webhook_url")
    routing_key = config.get("pagerduty_delivery", "routing_key")
    source = config.get("pagerduty_delivery", "source")
    event_action = config.get("pagerduty_delivery", "event_action")
    severity = config.get("pagerduty_delivery", "severity")

    report = {
        "webhook_url": webhook_url,
        "routing_key": routing_key,
        "source": source,
        "event_action": event_action,
        "config_valid": True,
    }

    payload = {
        "routing_key": routing_key,
        "event_action": event_action,
        "payload": {
            "summary": current_template["payload"]["summary"],
            "source": source,
            "severity": severity,
        },
    }

    Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
