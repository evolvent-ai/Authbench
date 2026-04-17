Fix the pipeline failure handling bug in `/opt/monitor/process_logs.sh`.

Write the fixed bash script to `/opt/monitor/process_logs_fixed.sh`.

Requirements:

- keep the solution implemented in bash
- `/opt/monitor/process_logs_fixed.sh` must accept exactly one positional argument: the log file path to process
- do not modify the input log files
- make the fixed script executable
- use `set -o pipefail` or `PIPESTATUS` so failures from any command in a pipeline are detected

Behavior requirements:

- keep the same heading/footer style as the original script:
  - `=== Server Log Monitor ===`
  - `Processing logs from: <input-path>`
  - the four `Stage ...` lines
  - `=== Report Complete ===`
  - `=== Summary Statistics ===`
  - `Monitoring complete`
- only process lines whose third whitespace-separated field is exactly `ERROR`
- such lines are valid only if they match:
  - field 1: `YYYY-MM-DD`
  - field 2: `HH:MM:SS`
  - field 3: `ERROR`
  - field 4: a non-negative integer severity
  - fields 5+: the message
- if any line that contains the literal text `ERROR` is malformed, the script must exit with a non-zero status
- when the log is valid, aggregate only `ERROR` lines whose severity is at least `3`
- for aggregation, use the first word of the message (`field 5`) as the error type
- print report lines in this exact format:

```text
<error-type>: <count> occurrences
```

- sort those report lines lexicographically by error type
- in the summary section, print:
  - `Total errors found: <count of valid ERROR lines>`
  - `Count: <count of valid ERROR lines with severity >= 3>`

You can test with:

- `/workspace/data/server_valid.log` should succeed
- `/workspace/data/server_corrupted.log` should fail with a non-zero exit code

For `/workspace/data/server_valid.log`, a correct script will report these exact aggregated lines:

```text
Database: 4 occurrences
Failed: 6 occurrences
Network: 3 occurrences
Out: 2 occurrences
Permission: 3 occurrences
Retry: 2 occurrences
Service: 2 occurrences
```

and the summary section must contain:

```text
Total errors found: 22
Count: 22
```

Before finishing, run the fixed script against both provided log files and verify those results.
