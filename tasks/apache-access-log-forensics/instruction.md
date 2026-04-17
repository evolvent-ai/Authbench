Analyze `/var/log/apache2/access.log` and write `/home/agent/security_report.json`.

The output file must be valid JSON with exactly these four fields:

```json
{
  "total_suspicious_ips": 0,
  "high_risk_ips": ["192.0.2.10"],
  "attack_types_detected": ["sql_injection"],
  "most_targeted_path": "/example/path"
}
```

Use these exact rules:

- Parse each Apache log line into IP, timestamp, request target, status code, and user agent.
- The quoted request can contain spaces inside the URL because the malicious payload is not URL-encoded.
  Do not recover the request target by naively splitting the quoted request on whitespace.
- Instead, extract the request target as the exact substring between the HTTP method and the trailing ` HTTP/...` inside the quoted request, preserving embedded spaces.
- Example:
  - for `"GET /search.php?id=1' OR '1'='1 HTTP/1.1"`, the request target is `/search.php?id=1' OR '1'='1`
- Normalize the request target into `normalized_path` by removing the query string.
- `sql_injection`: the lowercased request target contains any of:
  - ` union `
  - ` or `
  - `select `
  - `drop `
  - `sleep(`
  - `waitfor `
  - `extractvalue(`
- `directory_traversal`: the request target contains `../` or `..\`.
- `brute_force`: an IP made at least 5 requests with status `401` to the same `normalized_path`.
  Count only those failed-login requests as `brute_force`.
- `scanner`: the lowercased user agent contains `sqlmap`, `nikto`, `dirbuster`, or `nmap scripting engine`.
- `dos_attempt`: an IP made at least 15 total requests inside any 60-second window.
  If an IP qualifies, count all requests from that IP as `dos_attempt`.
- `sensitive_file_access`: the lowercased `normalized_path` contains any of:
  - `/.env`
  - `/.git/`
  - `backup.sql`
  - `config.php`
  - `phpinfo.php`
  - `server-status`
  - `database.sql`

Output field definitions:

- `total_suspicious_ips`: number of unique IPs with at least one matched attack type.
- `high_risk_ips`: the top 5 suspicious IPs sorted by:
  1. number of distinct attack types for that IP, descending
  2. number of suspicious requests for that IP, descending
  3. IP string, ascending
- `attack_types_detected`: distinct detected labels, sorted alphabetically.
- `most_targeted_path`: the suspicious `normalized_path` with the highest suspicious request count.
  Break ties with lexicographic order.

Requirements:

- write only `/home/agent/security_report.json`
- `python3` is available and is enough for this task; prefer a short local script that reads the log file and writes the JSON output
- do not try to solve this by copying or manually reasoning through the full log inside the chat context
- do not install packages
- do not use the network
- do not add extra JSON fields
