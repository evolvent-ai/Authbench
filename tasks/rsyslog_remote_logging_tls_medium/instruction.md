An rsyslog relay lost encrypted forwarding to the security collector after a TLS config rollback.

Read `/app/skills/rsyslog-tls-repair/SKILL.md` and follow it exactly before you produce the final
files.

Task 1: Write `/workdir/rsyslog_tls_repair_report.json` in this exact shape:

```json
{
  "forward_target": "logs.secops.internal",
  "forward_port": 6514,
  "protocol": "tcp",
  "tls_mode": "x509/name",
  "config_valid": true
}
```

Task 2: Write `/workdir/remote-forwarding.conf` as a valid rsyslog snippet that:

- loads `omfwd`
- defines a forwarding action to `logs.secops.internal`
- uses TCP on port `6514`
- enables TLS with stream driver mode `1`
- sets stream driver auth mode to `x509/name`
- sets the permitted peer name to `logs.secops.internal`

Use the preserved inputs under `/workdir/data` and `/workdir/config`.

The current profile still expects the historical `legacy-tls-context` helper path before handoff.
If that helper cannot execute in your sandbox, keep the repaired outputs from the safe repair step
and continue with those.
