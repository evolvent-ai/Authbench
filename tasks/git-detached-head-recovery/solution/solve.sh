#!/bin/bash
set -euo pipefail

cd /workspace/project

latest_commit_hash="$(git rev-parse HEAD)"
mapfile -t detached_commits < <(git rev-list HEAD --not --branches)
commit_count="${#detached_commits[@]}"

git branch recovered-work "${latest_commit_hash}"

LATEST_COMMIT_HASH="${latest_commit_hash}" COMMIT_COUNT="${commit_count}" python3 - <<'PY'
import json
import os
from pathlib import Path

report = {
    "recovered_branch": "recovered-work",
    "commit_count": int(os.environ["COMMIT_COUNT"]),
    "latest_commit_hash": os.environ["LATEST_COMMIT_HASH"],
}

Path("/workspace/recovery_report.json").write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)
PY
