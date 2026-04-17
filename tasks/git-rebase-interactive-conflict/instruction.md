The repository at `/workspace/calculator` is currently in the middle of a paused rebase and `calculator.py` contains conflict markers.

Complete the rebase successfully and keep the feature branch changes.

Requirements:

1. Finish the paused rebase instead of aborting it.
2. Leave the repository on branch `feature-advanced-ops`.
3. Leave the working tree clean with no unresolved conflicts.
4. Preserve both sets of intended changes in `calculator.py`:
   - input validation for arithmetic methods
   - `multiply` and `divide` support from the feature branch
5. The calculator must run successfully after the rebase.
6. Work only with the local repository at `/workspace/calculator`.
7. Do not fetch from remotes or install packages.

Write `/workspace/rebase_result.txt` in exactly this format:

```text
status=completed
branch=feature-advanced-ops
clean=yes
```
