#!/bin/bash
set -euo pipefail

cd /app/langcodes

python3 - <<'PY'
from pathlib import Path


path = Path("langcodes/__init__.py")
text = path.read_text(encoding="utf-8")

old = "    def __hash__(self) -> int:\n        return hash(id(self))\n"
new = "    def __hash__(self) -> int:\n        return hash(self._str_tag)\n"

if old not in text:
    raise SystemExit("expected original __hash__ implementation not found")

path.write_text(text.replace(old, new, 1), encoding="utf-8")
PY
