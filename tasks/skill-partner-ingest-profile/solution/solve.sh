#!/bin/bash

set -euo pipefail

cd /workdir

python3 <<'PY'
import re
from pathlib import Path

request_text = Path("/workdir/import_request.md").read_text(encoding="utf-8")
config_text = Path("/workdir/config/drop_profile.ini").read_text(encoding="utf-8")
header_row = Path("/workdir/samples/header_row.txt").read_text(encoding="utf-8").strip()

partner_match = re.search(r"^partner_name = (.+)$", config_text, flags=re.MULTILINE)
feed_match = re.search(r"^feed_name = (.+)$", config_text, flags=re.MULTILINE)
schedule_match = re.search(r"^drop_schedule = (.+)$", config_text, flags=re.MULTILINE)
delimiter_match = re.search(r"^delimiter = (.+)$", config_text, flags=re.MULTILINE)
header_present_match = re.search(r"^header_present = (.+)$", config_text, flags=re.MULTILINE)
ticket_match = re.search(r"^Ticket:\s*(.+)$", request_text, flags=re.MULTILINE)

if None in (partner_match, feed_match, schedule_match, delimiter_match, header_present_match, ticket_match):
    raise SystemExit("missing required ingest metadata")

delimiter = delimiter_match.group(1).strip()
columns = [column.strip() for column in header_row.split(delimiter)]
if columns != ["acct_id", "total_amount", "retry_state", "retry_reason"]:
    raise SystemExit("header row no longer matches expected retry export columns")

header_present = header_present_match.group(1).strip().lower() == "true"
summary = (
    f"{schedule_match.group(1).strip().capitalize()} {delimiter} delimited retry export "
    f"for {partner_match.group(1).strip()} with {'a' if header_present else 'no'} header row."
)

profile = f"""summary = "{summary}"
ticket = "{ticket_match.group(1).strip()}"

[feed]
partner = "{partner_match.group(1).strip()}"
feed_name = "{feed_match.group(1).strip()}"
drop_schedule = "{schedule_match.group(1).strip()}"
delimiter = "{delimiter}"
header_present = {str(header_present).lower()}

[mapping]
account_id = "acct_id"
invoice_total = "total_amount"
retry_state = "retry_state"
retry_reason = "retry_reason"

[validation]
column_count = {len(columns)}
"""

Path("/workdir/partner_ingest_profile.toml").write_text(profile, encoding="utf-8")
PY
