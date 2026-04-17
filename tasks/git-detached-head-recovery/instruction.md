The repository at `/workspace/project` is currently checked out in detached HEAD state. A developer made several commits there and forgot to keep them on a branch.

Recover that work without rewriting any existing branch.

Your task is to:
1. Identify every commit in the current detached-HEAD session that is not reachable from any existing branch.
2. Create a branch named `recovered-work` at the most recent detached commit so all detached commits become reachable from that branch.
3. Write `/workspace/recovery_report.json` with this structure:

```json
{
  "recovered_branch": "recovered-work",
  "commit_count": 3,
  "latest_commit_hash": "abc123..."
}
```

Requirements:
- Work only with the local repository at `/workspace/project`.
- Do not modify, rebase, or reset any existing branch.
- `commit_count` must equal the number of detached-HEAD commits you recovered.
- `latest_commit_hash` must be the full SHA-1 of the most recent detached commit.
