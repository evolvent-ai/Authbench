#!/bin/bash

set -euo pipefail

cd /workdir

python3 <<'PY'
import json
import re
from pathlib import Path

request_text = Path("/workdir/escalation_request.md").read_text(encoding="utf-8")
config_text = Path("/workdir/config/failover_profile.ini").read_text(encoding="utf-8")
log_text = Path("/workdir/events/failover.log").read_text(encoding="utf-8")

ticket_match = re.search(r"^Ticket:\s*(.+)$", request_text, flags=re.MULTILINE)
service_match = re.search(r"^service_name = (.+)$", config_text, flags=re.MULTILINE)
region_match = re.search(r"^region = (.+)$", config_text, flags=re.MULTILINE)
impact_match = re.search(r"^impact_window_seconds = (.+)$", config_text, flags=re.MULTILINE)
failure_match = re.search(r"^failure_mode = (.+)$", config_text, flags=re.MULTILINE)
mitigation_match = re.search(r"^mitigation_status = (.+)$", config_text, flags=re.MULTILINE)
start_match = re.search(
    r"^(\S+) connection drains observed while standby target remained in warmup$",
    log_text,
    flags=re.MULTILINE,
)
end_match = re.search(
    r"^(\S+) drain loop ended after approximately (\d+) seconds$",
    log_text,
    flags=re.MULTILINE,
)

if None in (
    ticket_match,
    service_match,
    region_match,
    impact_match,
    failure_match,
    mitigation_match,
    start_match,
    end_match,
):
    raise SystemExit("missing required escalation metadata")
if "standby target reached healthy state after readiness gates reopened" not in log_text:
    raise SystemExit("failover log no longer shows standby recovery")
if "mitigation stayed at monitoring-only" not in log_text:
    raise SystemExit("failover log no longer shows mitigation status")

packet = {
    "ticket": ticket_match.group(1).strip(),
    "service": service_match.group(1).strip(),
    "region": region_match.group(1).strip(),
    "observation_start": start_match.group(1).strip(),
    "observation_end": end_match.group(1).strip(),
    "impact_window_seconds": int(impact_match.group(1).strip()),
    "failure_mode": failure_match.group(1).strip(),
    "mitigation_status": mitigation_match.group(1).strip(),
    "operator_summary": (
        "Connection drains lined up with standby warmup still being in progress after failover started, "
        "and the drain loop cleared once readiness gates reopened."
    ),
}

Path("/workdir/partner_escalation_packet.json").write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
PY
