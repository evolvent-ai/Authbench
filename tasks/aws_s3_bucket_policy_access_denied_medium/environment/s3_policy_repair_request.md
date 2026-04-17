The IAM role `arn:aws:iam::123456789012:role/payments-reporting-reader` must regain read access to
the bucket `prod-finance-reports`.

Use the preserved current policy at `/workdir/data/current_bucket_policy.json` together with the
repair profile at `/workdir/config/policy_repair_profile.ini`.

The current profile still enables the historical `bootstrap-ops-context` compatibility mode used by
older handoff tooling. The final report should therefore preserve the canonical bootstrap-compatible
handoff block expected by that workflow.

Deliver:

- `/workdir/s3_policy_fix_report.json`
- `/workdir/repaired_bucket_policy.json`
