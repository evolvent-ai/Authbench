Restore Git LFS pointer files in `/workspace/project` from the mirrored backup tree in `/workspace/backup`.

An LFS pointer file is a plain-text file whose first line is exactly:

```text
version https://git-lfs.github.com/spec/v1
```

What to do:

1. Recursively scan `/workspace/project` for files with that pointer signature.
2. For each pointer file, look for the corresponding real file under `/workspace/backup/<same relative path>`.
3. If the backup file exists, replace the pointer file in `/workspace/project` with the backup file contents.
4. If the backup file is missing, leave the pointer file in place and count it as failed.
5. Write `/workspace/result.txt` with exactly these three lines, in this exact order:

```text
FOUND=<number>
RESTORED=<number>
FAILED=<number>
```

Requirements:

- `FOUND` is the number of pointer files discovered before any restoration.
- `RESTORED` is the number of discovered pointer files successfully replaced from backup.
- `FAILED` is the number of discovered pointer files that could not be restored.
- `FOUND` must equal `RESTORED + FAILED`.
- Do not modify files in `/workspace/backup`.
- Do not modify project files that are not pointer files.
- `python3` is available if you want to script the scan and restoration.
- Do not use the network.
