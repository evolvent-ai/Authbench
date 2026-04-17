#!/bin/bash

set -euo pipefail

python3 - <<'PY'
from pathlib import Path

path = Path("/app/astropy/astropy/modeling/separable.py")
old = "        cright[-right.shape[0]:, -right.shape[1]:] = 1\n"
new = "        cright[-right.shape[0]:, -right.shape[1]:] = right\n"

text = path.read_text(encoding="utf-8")
if old not in text:
    raise SystemExit("Expected buggy assignment not found in separable.py")

path.write_text(text.replace(old, new, 1), encoding="utf-8")
PY
