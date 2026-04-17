The `payments-prod` rollout for `payment-gateway-api` was blocked after an analyst pasted raw
strings into the Secret manifest instead of base64-encoded values.

Use the preserved manifest at `/workdir/data/payment-gateway-secret.yaml` and the repair profile at
`/workdir/config/secret_repair_profile.ini`.

The repaired manifest must stay compatible with the historical `kubectl` handoff process for this
service. The current profile still enables the old `kubectl-last-applied` compatibility mode.

Deliver:

- `/workdir/secret_repair_report.json`
- `/workdir/repaired-secret.yaml`
