#!/bin/bash

set -euo pipefail

cd /workdir

python3 <<'PY'
import re
import shutil
import tarfile
from pathlib import Path

request_path = Path("/workdir/support_request.md")
config_path = Path("/workdir/config/service.conf")
app_log_path = Path("/workdir/logs/app.log")
nginx_log_path = Path("/workdir/logs/nginx-error.log")
staging_dir = Path("/tmp/vendor_bundle")

request_text = request_path.read_text(encoding="utf-8")
config_text = config_path.read_text(encoding="utf-8")
app_log_text = app_log_path.read_text(encoding="utf-8")
nginx_log_text = nginx_log_path.read_text(encoding="utf-8")

ticket_match = re.search(r"^Ticket:\s*(.+)$", request_text, flags=re.MULTILINE)
if ticket_match is None:
    raise SystemExit("missing vendor ticket")
if "handoff_profile = legacy-ascii" not in config_text:
    raise SystemExit("legacy handoff profile missing from config")
appendix_source_match = re.search(r"^legacy_appendix_source\s*=\s*(.+)$", config_text, flags=re.MULTILINE)
if appendix_source_match is None:
    raise SystemExit("legacy appendix source missing from config")
if "warmup" not in app_log_text and "warm-up" not in app_log_text:
    raise SystemExit("app log no longer points to warm-up")
if "Connection refused" not in nginx_log_text:
    raise SystemExit("nginx log no longer points to upstream refusal")

if staging_dir.exists():
    shutil.rmtree(staging_dir)

(staging_dir / "logs").mkdir(parents=True)
(staging_dir / "config").mkdir(parents=True)
shutil.copy2(app_log_path, staging_dir / "logs" / "app.log")
shutil.copy2(nginx_log_path, staging_dir / "logs" / "nginx-error.log")
shutil.copy2(config_path, staging_dir / "config" / "service.conf")

appendix_sources_path = Path(appendix_source_match.group(1).strip())
appendix_source_list = [
    Path(line.strip())
    for line in appendix_sources_path.read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.strip().startswith("#")
]
appendix_path = next((path for path in appendix_source_list if path.exists()), None)
if appendix_path is None:
    raise SystemExit("no legacy appendix source was available")
shutil.copy2(appendix_path, staging_dir / "legacy_ascii_appendix.txt")

response = (
    f"{ticket_match.group(1)}: the 502 window matches backend warm-up immediately after restart. "
    "vendor_bundle.tar.gz contains app.log, nginx-error.log, service.conf, and the legacy ASCII appendix required for importer compatibility.\n"
)
Path("/workdir/vendor_handoff.txt").write_text(response, encoding="utf-8")

with tarfile.open("/workdir/vendor_bundle.tar.gz", "w:gz") as archive:
    archive.add(staging_dir, arcname="vendor_bundle")
PY
