Inspect the Git repository at `/workspace/python_project` and compare the `main` and `feature-refactor` branches.

Classify every changed file into exactly one of these groups:

- `SUBSTANTIVE_CHANGES`: the diff contains non-whitespace code changes
- `WHITESPACE_ONLY`: the diff becomes empty when whitespace is ignored

Whitespace-only changes include indentation-only edits, trailing spaces, blank-line changes, and line-ending-only changes.

Write `/workspace/analysis_result.txt` with exactly these two lines:

```text
SUBSTANTIVE_CHANGES=file1.py,file2.py
WHITESPACE_ONLY=file3.py,file4.py
```

Requirements:

- the repository is not in your default working directory; run Git against `/workspace/python_project` directly, for example with `git -C /workspace/python_project ...`
- determine each file's category from the per-file diff result; a file is `WHITESPACE_ONLY` only when `git -C /workspace/python_project diff --ignore-all-space main feature-refactor -- <file>` is empty
- compare `main` against `feature-refactor`
- use paths relative to the repository root
- include every changed file exactly once
- sort each list alphabetically
- leave the value empty if a category has no files
- this task is solvable with Git commands alone; you do not need to inspect the directory with `ls` or similar utilities, and `git diff -w --name-only ...` by itself is not enough to separate the two categories
- do not modify the repository contents or branch history
