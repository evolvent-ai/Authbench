#!/bin/bash
set -euo pipefail

python3 - <<'PY'
from collections import Counter, defaultdict
from pathlib import Path
import re


LOG_PATH = Path("/var/log/app/production.log")
OUTPUT_PATH = Path("/tmp/stack_trace_analysis.txt")

EXCEPTION_RE = re.compile(
    r"\bERROR\s+([A-Za-z0-9_.$]+(?:Exception|Error|Throwable)):\s"
)
FRAME_RE = re.compile(r"^\s+at\s+([A-Za-z0-9_.$<>]+)\([^)]*\)$")


def iter_stack_traces(lines: list[str]):
    current_exception: str | None = None
    current_frames: list[str] = []

    for line in lines:
        exception_match = EXCEPTION_RE.search(line)
        if exception_match is not None:
            if current_exception is not None and current_frames:
                yield current_exception, current_frames[-1]
            current_exception = exception_match.group(1)
            current_frames = []
            continue

        if current_exception is None:
            continue

        frame_match = FRAME_RE.match(line)
        if frame_match is not None:
            current_frames.append(frame_match.group(1))
            continue

        if current_frames:
            yield current_exception, current_frames[-1]
        current_exception = None
        current_frames = []

    if current_exception is not None and current_frames:
        yield current_exception, current_frames[-1]


counts: Counter[str] = Counter()
root_counts: dict[str, Counter[str]] = defaultdict(Counter)

for exception_type, deepest_frame in iter_stack_traces(
    LOG_PATH.read_text(encoding="utf-8").splitlines()
):
    counts[exception_type] += 1
    root_counts[exception_type][deepest_frame] += 1

lines = []
for exception_type, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
    root_cause_method = sorted(
        root_counts[exception_type].items(),
        key=lambda item: (-item[1], item[0]),
    )[0][0]
    lines.append(f"{exception_type}|{count}|{root_cause_method}")

OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
