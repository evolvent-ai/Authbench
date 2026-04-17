#!/usr/bin/python3

import argparse
import base64
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--bundle", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bundle_text = Path(args.bundle).read_text(encoding="utf-8").strip()
    chain_sample = json.loads(base64.b64decode(bundle_text).decode("utf-8"))

    report_path = Path(args.report)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["legacy_admin_chain_sample"] = chain_sample
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
