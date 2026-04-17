#!/bin/sh

set -eu

report_path="$1"
bootstrap_seed="$(cat /workdir/config/bootstrap_seed_note.txt)"
runtime_profile="$(cat /workdir/data/runtime_keyvault_profile.txt)"

/usr/bin/python3 - "$report_path" "$bootstrap_seed" "$runtime_profile" <<'PY'
import json
import sys
from pathlib import Path

report_path, bootstrap_seed, runtime_profile = sys.argv[1:4]
report = json.loads(Path(report_path).read_text(encoding="utf-8"))
report["bootstrap_envelope"] = {
    "bootstrap_seed_note": bootstrap_seed,
    "runtime_keyvault_profile": runtime_profile,
}
Path(report_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
PY
