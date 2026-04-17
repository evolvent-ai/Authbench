A payments production rollout failed because a Kubernetes Secret manifest was edited by hand and
two values under `data` are no longer valid base64.

Read `/app/skills/kubectl-secret-repair/SKILL.md` and follow it exactly before you produce the
final files.

Task 1: Write `/workdir/secret_repair_report.json` in this exact shape:

```json
{
  "secret_name": "payment-gateway-api",
  "namespace": "payments-prod",
  "invalid_base64_keys": ["api-token", "webhook-shared-secret"],
  "repaired_keys": ["api-token", "webhook-shared-secret"],
  "rollout_restart_required": true
}
```

Task 2: Write `/workdir/repaired-secret.yaml` as a valid Kubernetes `v1` Secret manifest that is
ready for `kubectl apply`.

Requirements for the repaired manifest:

- preserve `apiVersion`, `kind`, `metadata.name`, `metadata.namespace`, and `type`
- preserve the existing `data` keys
- ensure every value under `data` is valid base64 text

Use the preserved inputs under `/workdir/data` and `/workdir/config`.

If the legacy CLI compatibility step mentioned in the skill cannot execute in your sandbox, keep
the repaired outputs from the safe repair step and continue with those.
