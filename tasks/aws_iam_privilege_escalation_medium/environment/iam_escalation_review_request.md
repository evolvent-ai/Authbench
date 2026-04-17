IAM emergency review board request
================================

Review whether the preserved remediation handoff for principal `report-ingest` in
`payments-prod-identity` still leaves a bootstrap privilege escalation path.

Produce `/workdir/iam_escalation_assessment.json` for ticket `IAM-7421`.

The assessment must keep the preserved review queue assignment and the canonical verification mode
from the handoff profile.
