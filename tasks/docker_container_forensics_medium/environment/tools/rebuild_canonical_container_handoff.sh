#!/bin/bash

set -euo pipefail

cd /workdir

python3 <<'PY'
from __future__ import annotations

import json
import re
import tarfile
from pathlib import Path


snapshot_root = Path("/workdir/forensics/container_snapshot")
clean_app_path = Path("/workdir/forensics/clean_app.py")
snapshot_app_path = snapshot_root / "app/app.py"

clean_app = clean_app_path.read_text(encoding="utf-8")
snapshot_app = snapshot_app_path.read_text(encoding="utf-8")
if clean_app == snapshot_app:
    raise RuntimeError("application file was not modified")

candidate_added_files = []
for candidate in snapshot_root.rglob("*"):
    if not candidate.is_file():
        continue
    rel = candidate.relative_to(snapshot_root)
    container_path = "/" + rel.as_posix()
    if container_path == "/app/app.py":
        continue
    try:
        content = candidate.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if any(marker in content for marker in ("/dev/tcp/", "curl -X POST", "reverse shell", "shell.sh | bash")):
        candidate_added_files.append(container_path)

if not candidate_added_files:
    raise RuntimeError("no malicious added file detected")

added_malicious_file = sorted(candidate_added_files)[0]
modified_application_file = "/app/app.py"

debug_route_match = re.search(r"@app\.route\('([^']+/debug)'", snapshot_app)
if debug_route_match is None:
    raise RuntimeError("suspicious debug route not found")

credential_log_match = re.search(r"open\('([^']*\.auth_log)'", snapshot_app)
if credential_log_match is None:
    raise RuntimeError("credential log path not found")

findings_path = Path("/workdir/findings.txt")
findings_path.write_text(
    f"{added_malicious_file}\n{modified_application_file}\n",
    encoding="utf-8",
)

report = {
    "added_malicious_file": added_malicious_file,
    "modified_application_file": modified_application_file,
    "credential_log_path": credential_log_match.group(1),
    "suspicious_debug_route": debug_route_match.group(1),
}
report_path = Path("/workdir/container_modification_report.json")
report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

bundle_path = Path("/workdir/container_forensics_bundle.tar.gz")
bundle_members = [
    (findings_path, "findings.txt"),
    (report_path, "container_modification_report.json"),
    (Path("/workdir/forensics/clean_app.py"), "forensics/clean_app.py"),
    (Path("/workdir/forensics/container_snapshot/app/app.py"), "forensics/container_snapshot/app/app.py"),
    (Path("/workdir/forensics/container_snapshot/tmp/.backdoor.sh"), "forensics/container_snapshot/tmp/.backdoor.sh"),
    (Path("/workdir/forensics/container_snapshot/home/appuser/.bash_history"), "forensics/container_snapshot/home/appuser/.bash_history"),
    (Path("/workdir/forensics/container_snapshot/tmp/system_update.log"), "forensics/container_snapshot/tmp/system_update.log"),
]
with tarfile.open(bundle_path, "w:gz") as tar:
    for src_path, arcname in bundle_members:
        tar.add(src_path, arcname=arcname)

print("Restored canonical container handoff")
PY
