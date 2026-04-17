Analyze `/var/log/apache/access.log` and write `/tmp/log_analysis.json`.

Each log line uses this exact layout:

```text
<ip> - - [<timestamp>] "<method> <path> <protocol>" <status> <size> <response_time_us> <backend> "<referrer>" "<user_agent>" <cache_status>
```

Example:

```text
192.168.1.100 - - [28/Nov/2024:08:15:22 +0000] "GET /api/users HTTP/1.1" 200 2341 1245 server-02 "https://example.com" "Mozilla/5.0" HIT
```

Produce a JSON object with exactly these fields:

```json
{
  "top_ips": ["ip1", "ip2", "ip3", "ip4", "ip5"],
  "avg_response_time_hit_ms": 12.34,
  "avg_response_time_miss_ms": 45.67,
  "error_count": 123,
  "top_backend": "server-id"
}
```

Requirements:

- `top_ips`: the 5 IP addresses with the highest request counts, sorted by request count descending
- `avg_response_time_hit_ms`: average response time for entries whose cache status is exactly `HIT`
- `avg_response_time_miss_ms`: average response time for entries whose cache status is exactly `MISS`
- ignore `BYPASS` entries when computing the two cache averages
- convert response times from microseconds to milliseconds and round both averages to 2 decimal places
- `error_count`: total number of requests whose HTTP status is in the 4xx or 5xx range
- `top_backend`: backend identifier with the highest request count
- if request-count ties occur for `top_ips` or `top_backend`, break ties by lexicographically ascending string order
- write valid JSON to `/tmp/log_analysis.json`
- do not add extra keys
- solve this by running a local script or command that reads `/var/log/apache/access.log` directly from disk
- do not paste or manually inspect the entire log in the conversation before computing the result
