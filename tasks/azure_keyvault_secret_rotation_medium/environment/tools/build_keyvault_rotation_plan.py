import argparse
import configparser
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--payload", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = json.loads(Path(args.metadata).read_text(encoding="utf-8"))

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")
    rotation = config["rotation"]

    report = {
        "vault_name": metadata["vault_name"],
        "secret_name": metadata["secret_name"],
        "current_version": metadata["current_version"],
        "new_version_alias": rotation["new_version_alias"],
        "retire_previous_after": rotation["retire_previous_after"],
        "content_type": metadata["content_type"],
    }

    payload = {
        "value": "ROTATION-TO-BE-INJECTED-BY-OPS",
        "contentType": metadata["content_type"],
        "attributes": {
            "enabled": True,
        },
        "tags": {
            "rotation_ticket": rotation["rotation_ticket"],
            "owner": metadata["owner"],
            "supersedes_version": metadata["current_version"],
            "new_version_alias": rotation["new_version_alias"],
        },
    }

    Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    Path(args.payload).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
