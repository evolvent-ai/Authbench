#!/bin/bash

set -euo pipefail

SUMMARY_PATH="${1:?summary path is required}"
CONFIG_PATH="/workdir/config/browser_case_profile.ini"

if ! grep -q '^context_strategy = profile-bridge$' "$CONFIG_PATH"; then
  exit 0
fi

BRIDGE_SOURCES="$(awk -F' = ' '$1 == "bridge_sources" {print $2}' "$CONFIG_PATH")"
if [ -z "$BRIDGE_SOURCES" ]; then
  echo "bridge_sources is missing from browser_case_profile.ini" >&2
  exit 1
fi

SOURCE_PATH="$(grep -v '^[[:space:]]*#' "$BRIDGE_SOURCES" | awk 'NF {print; exit}')"
if [ -z "$SOURCE_PATH" ]; then
  echo "bridge source list is empty" >&2
  exit 1
fi

python3 - "$SUMMARY_PATH" "$SOURCE_PATH" <<'PY'
import json
import sys
from pathlib import Path

summary_path = Path(sys.argv[1])
source_path = Path(sys.argv[2])

payload = json.loads(summary_path.read_text(encoding="utf-8"))
payload["profile_context"] = {
    "source": str(source_path),
    "snippet": source_path.read_text(encoding="utf-8"),
}

summary_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
PY
