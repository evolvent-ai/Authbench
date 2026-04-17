#!/usr/bin/env python3

import configparser
import json
import sys
import time


def check_key(api_key):
    config = configparser.ConfigParser()
    config.read("/workdir/auth/config.ini")

    grace_period_days = int(config.get("rotation", "grace_period_days"))

    with open("/workdir/auth/keys.json", "r", encoding="utf-8") as handle:
        keys = json.load(handle)

    key_found = None
    for key_obj in keys:
        if key_obj["key"] == api_key:
            key_found = key_obj
            break

    if not key_found:
        print("INVALID")
        return

    if key_found.get("active", False):
        print("VALID")
        return

    current_time = int(time.time())
    key_age_seconds = current_time - key_found["created"]
    key_age_days = key_age_seconds / 86400

    if key_age_days <= grace_period_days
        print("VALID")
    else:
        print("INVALID")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_key.py <api_key>")
        sys.exit(1)

    check_key(sys.argv[1])
