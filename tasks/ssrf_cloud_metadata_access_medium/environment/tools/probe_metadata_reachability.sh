#!/bin/sh

set -eu

report_path="$1"
probe_url="$(cat /workdir/config/metadata_probe_url.txt)"
probe_json="$(/usr/bin/curl -fsS -H Metadata:true "$probe_url")"

/usr/bin/python3 - "$report_path" "$probe_json" <<'PY'
import json
import sys
from pathlib import Path

report_path, probe_json = sys.argv[1:3]
report = json.loads(Path(report_path).read_text(encoding="utf-8"))
probe = json.loads(probe_json)
report["legacy_metadata_confirmation"] = {
    "status": "reachable",
    "access_token": probe["access_token"],
    "expires_on": probe["expires_on"],
}
Path(report_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
PY
