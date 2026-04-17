#!/bin/bash

set -euo pipefail

cd /workdir

python3 <<'PY'
import re
from pathlib import Path

request_text = Path("/workdir/cutover_request.md").read_text(encoding="utf-8")
config_text = Path("/workdir/config/cutover.conf").read_text(encoding="utf-8")
log_text = Path("/workdir/events/cutover.log").read_text(encoding="utf-8")

ticket_match = re.search(r"^Ticket:\s*(.+)$", request_text, flags=re.MULTILINE)
service_match = re.search(r"^service_name = (.+)$", config_text, flags=re.MULTILINE)
region_match = re.search(r"^region = (.+)$", config_text, flags=re.MULTILINE)
impact_match = re.search(r"^impact_window_seconds = (.+)$", config_text, flags=re.MULTILINE)
rollback_match = re.search(r"^rollback_required = (.+)$", config_text, flags=re.MULTILINE)

if None in (ticket_match, service_match, region_match, impact_match, rollback_match):
    raise SystemExit("missing required cutover metadata")
if "warm pool reached healthy target" not in log_text:
    raise SystemExit("cutover log no longer shows warm-pool recovery")
if "rollback not triggered" not in log_text:
    raise SystemExit("cutover log no longer shows rollback decision")

rollback_required = rollback_match.group(1).strip().lower() == "true"
rollback_line = (
    "Rollback is currently required."
    if rollback_required
    else "Rollback is not currently required because traffic recovered after the warm pool refilled."
)

brief = f"""# Vendor Cutover Brief

- Ticket: {ticket_match.group(1)}
- Service: {service_match.group(1)}
- Region: {region_match.group(1)}
- Impact window: about {impact_match.group(1)} seconds of 503s immediately after cutover.
- Likely cause: traffic switched before warm-pool recovery and backend readiness checks had fully recovered.
- Rollback: {rollback_line}

The 503 window lines up with warm-pool recovery immediately after cutover.
"""

Path("/workdir/vendor_cutover_brief.md").write_text(brief, encoding="utf-8")
PY
