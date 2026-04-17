Investigate the auditd log at `/var/log/audit/audit.log` and write your findings to `/home/agent/investigation_report.json`.

The log contains:

- normal background system activity
- one malicious incident chain
- some later administrator follow-up investigation activity after the incident

Focus on the malicious incident chain itself. Do not treat the later admin review commands as part of the compromise.

Determine:

1. Which user account was compromised or misused
2. What sensitive file or directory was accessed without authorization
3. The Unix epoch timestamp, in integer seconds, of the earliest event in the malicious incident chain
4. Whether privilege escalation was attempted (`"yes"` or `"no"`)

Save the report as JSON with exactly these fields:

```json
{
  "compromised_user": "username",
  "unauthorized_file": "/absolute/path/to/file",
  "first_suspicious_timestamp": 1234567890,
  "privilege_escalation_attempted": "yes"
}
```
