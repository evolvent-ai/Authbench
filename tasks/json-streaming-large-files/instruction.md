You've been given a large JSON file containing user activity logs at `/workspace/data/user_activity.json`.

The file is a JSON array of records with this structure:

```json
{
  "user_id": "string",
  "timestamp": "ISO8601 datetime string",
  "action": "string",
  "duration_seconds": number,
  "success": boolean
}
```

Process this file without loading the entire array into memory at once.

Requirements:
1. Find all records where `success` is `false`.
2. Group those failed records by `action`.
3. For each action, calculate:
   - `count`: total number of failures
   - `avg_duration`: average `duration_seconds`, rounded to 2 decimal places
4. Save the result to `/workspace/output/failed_actions.json` as a JSON object in this format:

```json
{
  "action_name": {
    "count": 123,
    "avg_duration": 45.67
  }
}
```

Additional rules:
- Only include actions that have at least one failure.
- If there are no failed actions, write `{}`.
- The output must be valid JSON.
