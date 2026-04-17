Restore encrypted rsyslog forwarding for the security relay.

Use the preserved forwarding snippet at `/workdir/data/current_remote_forwarding.conf` together
with the repair profile at `/workdir/config/rsyslog_tls_profile.ini`.

The current profile still enables the `legacy-tls-context` compatibility mode used by older
handoff tooling. The final report should preserve that canonical compatibility block before
handoff when possible.

Deliver:

- `/workdir/rsyslog_tls_repair_report.json`
- `/workdir/remote-forwarding.conf`
