#!/usr/bin/env python3

import argparse
import base64
import configparser
import json
from pathlib import Path


def parse_simple_secret(path: Path) -> tuple[dict[str, str], list[tuple[str, str]]]:
    metadata: dict[str, str] = {}
    data_entries: list[tuple[str, str]] = []
    document = {
        "apiVersion": "",
        "kind": "",
        "type": "",
    }
    section = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line == "metadata:":
            section = "metadata"
            continue
        if line == "data:":
            section = "data"
            continue
        if not line.startswith("  "):
            section = ""
            key, value = line.split(": ", 1)
            document[key] = value
            continue
        key, value = line.strip().split(": ", 1)
        if section == "metadata":
            metadata[key] = value
        elif section == "data":
            data_entries.append((key, value))
    return {
        "apiVersion": document["apiVersion"],
        "kind": document["kind"],
        "type": document["type"],
        "name": metadata["name"],
        "namespace": metadata["namespace"],
    }, data_entries


def is_valid_base64(value: str) -> bool:
    try:
        base64.b64decode(value.encode("utf-8"), validate=True)
    except Exception:
        return False
    return True


def render_secret(document: dict[str, str], data_entries: list[tuple[str, str]]) -> str:
    lines = [
        f"apiVersion: {document['apiVersion']}",
        f"kind: {document['kind']}",
        "metadata:",
        f"  name: {document['name']}",
        f"  namespace: {document['namespace']}",
        f"type: {document['type']}",
        "data:",
    ]
    for key, value in data_entries:
        lines.append(f"  {key}: {value}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    document, data_entries = parse_simple_secret(Path(args.input))

    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")
    rollout_restart_required = config.getboolean("secret_repair", "rollout_restart_required")

    invalid_keys: list[str] = []
    repaired_keys: list[str] = []
    rendered_data: list[tuple[str, str]] = []
    for key, value in data_entries:
        if is_valid_base64(value):
            rendered_data.append((key, value))
            continue
        invalid_keys.append(key)
        repaired_keys.append(key)
        rendered_data.append(
            (key, base64.b64encode(value.encode("utf-8")).decode("utf-8"))
        )

    report = {
        "secret_name": document["name"],
        "namespace": document["namespace"],
        "invalid_base64_keys": invalid_keys,
        "repaired_keys": repaired_keys,
        "rollout_restart_required": rollout_restart_required,
    }

    Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    Path(args.output).write_text(render_secret(document, rendered_data), encoding="utf-8")


if __name__ == "__main__":
    main()
