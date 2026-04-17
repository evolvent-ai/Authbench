import argparse
import configparser
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runtime = json.loads(Path(args.runtime).read_text(encoding="utf-8"))

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")

    assessment = {
        "service_name": runtime["service_name"],
        "risk_level": runtime["risk_level"],
        "metadata_endpoint": runtime["metadata_endpoint"],
        "verification_mode": config["assessment"]["verification_mode"],
        "recommended_action": runtime["recommended_action"],
        "next_step": runtime["next_step"],
    }
    Path(args.output).write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
