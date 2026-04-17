Prepare the filtered CloudTrail review requested in `/workdir/filter_case_request.md`.

Read the task-local skill `cloudtrail-filter-ops` at
`/app/skills/cloudtrail-filter-ops/SKILL.md` and use that workflow.
Ground the result in `/workdir/config/filter_profile.ini` and the preserved log files under
`/workdir/data/cloudtrail_logs/`.

Deliverables:

1. Write `/workdir/cloudtrail_filter_report.json` as a JSON object that includes at least:

```json
{
  "filter_name": "public-ip-credential-sequence",
  "compromised_user": "username",
  "suspicious_source_ip": "198.51.100.10",
  "first_match_time": "2024-01-15T17:11:09Z",
  "matched_event_count": 5,
  "target_resource": "arn:aws:s3:::bucket/key"
}
```

2. Write `/workdir/filtered_events.csv` with this exact header:

```csv
timestamp,event_name,source_ip,outcome,resource
```

The CSV must contain exactly the five filtered events that make up the suspicious external-IP
sequence, sorted by ascending timestamp.
