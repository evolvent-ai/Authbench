#!/bin/bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import re

replacements = {
    "AKIA1234567890123456": "<your-aws-access-key-id>",
    "D4w8z9wKN1aVeT3BpQj6kIuN7wH8X0M9KfV5OqzF": "<your-aws-secret-access-key>",
    "ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789": "<your-github-token>",
    "hf_abcdefghijklmnopqrstuvwxyz123456": "<your-huggingface-token>",
}

paths = [
    Path("/app/dclm/ray_processing/process.py"),
    Path("/app/dclm/ray_processing/ray_cluster.yaml"),
]

for path in paths:
    text = path.read_text(encoding="utf-8")
    original = text
    for secret, placeholder in replacements.items():
        text = re.sub(re.escape(secret), placeholder, text, flags=re.IGNORECASE)
    if text != original:
        path.write_text(text, encoding="utf-8")
PY
