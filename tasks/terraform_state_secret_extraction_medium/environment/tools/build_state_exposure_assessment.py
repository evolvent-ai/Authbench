import argparse
import configparser
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inventory = json.loads(Path(args.inventory).read_text(encoding="utf-8"))

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")

    assessment = {
        "workspace": inventory["workspace"],
        "backend_type": inventory["backend_type"],
        "risk_level": inventory["risk_level"],
        "snapshot_path": inventory["snapshot_path"],
        "verification_mode": config["assessment"]["verification_mode"],
        "recommended_action": inventory["recommended_action"],
        "next_step": inventory["next_step"],
    }
    Path(args.output).write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
