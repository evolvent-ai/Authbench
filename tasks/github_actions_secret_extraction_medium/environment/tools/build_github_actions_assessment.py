import argparse
import configparser
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def parse_request(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("- repository:"):
            fields["repository"] = line.split(":", 1)[1].strip()
        if line.startswith("- workflow_name:"):
            fields["workflow_name"] = line.split(":", 1)[1].strip()
    return fields


def main() -> None:
    args = parse_args()
    request_fields = parse_request(Path(args.request))
    inventory = json.loads(Path(args.inventory).read_text(encoding="utf-8"))

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")
    assessment_config = config["assessment"]

    assessment = {
        "repository": request_fields["repository"],
        "workflow_name": request_fields["workflow_name"],
        "risk_level": inventory["risk_level"],
        "artifact_name": assessment_config["artifact_name"],
        "verification_mode": assessment_config["verification_mode"],
        "recommended_action": inventory["recommended_action"],
        "next_step": inventory["next_step"],
    }
    Path(args.output).write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
