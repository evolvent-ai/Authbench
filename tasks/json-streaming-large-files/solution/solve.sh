#!/bin/bash

set -euo pipefail

mkdir -p /workspace/output

python3 - <<'PY'
import json
from pathlib import Path

INPUT_PATH = Path("/workspace/data/user_activity.json")
OUTPUT_PATH = Path("/workspace/output/failed_actions.json")


def iter_json_array(path: Path, chunk_size: int = 8192):
    decoder = json.JSONDecoder()
    buffer = ""
    pos = 0
    array_started = False

    with path.open("r", encoding="utf-8") as handle:
        while True:
            chunk = handle.read(chunk_size)
            eof = chunk == ""
            if not eof:
                buffer += chunk

            while True:
                while pos < len(buffer) and buffer[pos].isspace():
                    pos += 1

                if not array_started:
                    if pos >= len(buffer):
                        break
                    if buffer[pos] != "[":
                        raise ValueError("Expected JSON array")
                    array_started = True
                    pos += 1
                    continue

                while pos < len(buffer) and buffer[pos].isspace():
                    pos += 1

                if pos < len(buffer) and buffer[pos] == "]":
                    return

                if pos >= len(buffer):
                    break

                try:
                    item, next_pos = decoder.raw_decode(buffer, pos)
                except json.JSONDecodeError:
                    if eof:
                        raise
                    break

                yield item
                pos = next_pos

                while pos < len(buffer) and buffer[pos].isspace():
                    pos += 1

                if pos < len(buffer) and buffer[pos] == ",":
                    pos += 1
                    continue
                if pos < len(buffer) and buffer[pos] == "]":
                    return
                if eof:
                    break
                break

            if pos:
                buffer = buffer[pos:]
                pos = 0

            if eof:
                if not buffer.strip():
                    return
                # Let the outer loop surface any malformed trailing content.
                while buffer and buffer[0].isspace():
                    buffer = buffer[1:]
                if buffer == "]":
                    return
                if not buffer:
                    return


counts: dict[str, int] = {}
totals: dict[str, float] = {}

for record in iter_json_array(INPUT_PATH):
    if record.get("success") is not False:
        continue

    action = record.get("action")
    duration = float(record.get("duration_seconds", 0) or 0)

    if action not in counts:
        counts[action] = 0
        totals[action] = 0.0

    counts[action] += 1
    totals[action] += duration

result = {
    action: {
        "count": counts[action],
        "avg_duration": round(totals[action] / counts[action], 2),
    }
    for action in sorted(counts)
}

OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
PY
