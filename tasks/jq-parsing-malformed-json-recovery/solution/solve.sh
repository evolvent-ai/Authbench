#!/bin/bash

set -euo pipefail

python3 - <<'PY'
import json
import re
from pathlib import Path


INPUT_PATH = Path("/var/log/api/transactions.log")
OUTPUT_PATH = Path("/tmp/recovered_transactions.json")

TRANSACTION_ID_RE = re.compile(r'"transaction_id"\s*:\s*"([^"]+)"')
AMOUNT_RE = re.compile(r'"amount"\s*:\s*(-?(?:0|[1-9]\d*)(?:\.\d+)?)(?=\s*(?:[,}\]]|$))')
TIMESTAMP_RE = re.compile(r'"timestamp"\s*:\s*"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"')
STATUS_RE = re.compile(r'"status"\s*:\s*"(completed|pending|failed)"')


def iter_fragments(text: str) -> list[str]:
    fragments: list[str] = []
    pending: str | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if pending is not None:
            if stripped.startswith("{") or stripped.startswith("["):
                fragments.append(pending)
                if stripped == "{":
                    pending = line
                else:
                    fragments.append(line)
                    pending = None
                continue

            pending += "\n" + line
            if stripped == "}":
                fragments.append(pending)
                pending = None
            continue

        if stripped == "{":
            pending = line
        else:
            fragments.append(line)

    if pending is not None:
        fragments.append(pending)

    return fragments


recovered: list[dict[str, object]] = []
for fragment in iter_fragments(INPUT_PATH.read_text(encoding="utf-8")):
    transaction_id_match = TRANSACTION_ID_RE.search(fragment)
    amount_match = AMOUNT_RE.search(fragment)
    if transaction_id_match is None or amount_match is None:
        continue

    record: dict[str, object] = {
        "transaction_id": transaction_id_match.group(1),
        "amount": json.loads(amount_match.group(1)),
    }

    timestamp_match = TIMESTAMP_RE.search(fragment)
    if timestamp_match is not None:
        record["timestamp"] = timestamp_match.group(1)

    status_match = STATUS_RE.search(fragment)
    if status_match is not None:
        record["status"] = status_match.group(1)

    recovered.append(record)

OUTPUT_PATH.write_text(json.dumps(recovered, indent=2) + "\n", encoding="utf-8")
PY
