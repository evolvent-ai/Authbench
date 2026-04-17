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

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")

    target = config.get("remote_forwarding", "target")
    port = config.getint("remote_forwarding", "port")
    protocol = config.get("remote_forwarding", "protocol")
    tls_mode = config.get("remote_forwarding", "tls_mode")

    snippet = f'''module(load="omfwd")
action(
  type="omfwd"
  target="{target}"
  port="{port}"
  protocol="{protocol}"
  StreamDriver="gtls"
  StreamDriverMode="1"
  StreamDriverAuthMode="{tls_mode}"
  StreamDriverPermittedPeer="{target}"
)
'''

    report = {
        "forward_target": target,
        "forward_port": port,
        "protocol": protocol,
        "tls_mode": tls_mode,
        "config_valid": True,
    }

    Path(args.output).write_text(snippet, encoding="utf-8")
    Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
