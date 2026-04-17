Fix the whitespace-handling bug in `/opt/data_processor/process_records.sh`.

The script reads `/opt/data_processor/sample_data.csv`, builds `/opt/data_processor/report.txt`, and writes progress lines to a temp file before appending them to the report.

The current problem is that the script uses unsafe unquoted expansions in several places. The task data contains multi-word names and addresses such as `John Smith` and `123 Main Street`, and the script must preserve those fields exactly.

Requirements:

- keep the task implemented in bash
- fix the existing script in place at `/opt/data_processor/process_records.sh`
- keep the current report format, but make the field handling safe
- after your fix, running `/opt/data_processor/process_records.sh` must succeed and generate `/opt/data_processor/report.txt`
- customer names and addresses with spaces must stay intact in the report and appended processing lines

Create `/solution/fix_summary.txt` with exactly two lines:

```text
ISSUE=<one-line root cause>
LINES_MODIFIED=<comma-separated line numbers>
```

Example:

```text
ISSUE=Unquoted expansions made field handling whitespace-sensitive
LINES_MODIFIED=13,15,31
```

Do not move files to other paths.
