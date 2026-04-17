#!/bin/bash

set -euo pipefail

python3 - <<'PY'
from pathlib import Path

path = Path("/app/astropy/astropy/io/ascii/qdp.py")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        "    _line_type_re = re.compile(_type_re)\n",
        "    _line_type_re = re.compile(_type_re, re.IGNORECASE)\n",
    ),
    (
        "            if v == \"NO\":\n",
        "            if v.upper() == \"NO\":\n",
    ),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f"Expected buggy snippet not found: {old!r}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
PY
