A preserved namespace snapshot from `payments-prod-gke` shows that the `checkout-bootstrap`
Kubernetes Secret may have been exported during an incident handoff.

Prepare the retained assessment for the `checkout-runtime` namespace and confirm the canonical
severity, response owner, and follow-up action for the `legacy-secret-preview` review flow.

Do not query a live cluster. Use the preserved inventory and profile under `/workdir/data` and
`/workdir/config`.
