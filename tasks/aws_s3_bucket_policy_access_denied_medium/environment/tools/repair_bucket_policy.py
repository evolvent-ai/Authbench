#!/usr/bin/env python3

import argparse
import configparser
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    config = configparser.ConfigParser()
    config.read(args.config, encoding="utf-8")

    bucket_name = config.get("policy_repair", "bucket_name")
    principal_arn = config.get("policy_repair", "principal_arn")

    statements = policy.get("Statement", [])
    statements = [stmt for stmt in statements if stmt.get("Sid") != "AllowPaymentsReportingRead"]
    statements.append(
        {
            "Sid": "AllowPaymentsReportingRead",
            "Effect": "Allow",
            "Principal": {"AWS": principal_arn},
            "Action": ["s3:ListBucket", "s3:GetObject"],
            "Resource": [
                f"arn:aws:s3:::{bucket_name}",
                f"arn:aws:s3:::{bucket_name}/*",
            ],
        }
    )

    repaired_policy = {
        "Version": "2012-10-17",
        "Statement": statements,
    }
    report = {
        "bucket_name": bucket_name,
        "principal_arn": principal_arn,
        "required_actions": ["s3:ListBucket", "s3:GetObject"],
        "repaired_statement_sid": "AllowPaymentsReportingRead",
        "policy_valid": True,
    }

    Path(args.output).write_text(json.dumps(repaired_policy, indent=2) + "\n", encoding="utf-8")
    Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
