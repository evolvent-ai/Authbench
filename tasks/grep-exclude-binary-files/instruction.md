Audit `/workspace/project` and create a reusable grep configuration that makes recursive searches safe in the presence of binary files.

Your goals:
- identify all binary files currently present in `/workspace/project`
- create a configuration file for grep
- verify that searching for `TODO` across the repository only returns text-file matches

Requirements:
- save the final report to `/workspace/solution.txt`
- the report must contain exactly these three lines:
  `BINARY_COUNT=<number>`
  `CONFIG_FILE=<absolute path>`
  `TEST_RESULT=<SUCCESS or FAILURE>`
- the configuration file must be reusable rather than a one-off shell alias
- the configuration file must contain one grep CLI option per line
- the configuration must be usable with this style of invocation:
  `grep $(tr '\n' ' ' < "$CONFIG_FILE") -r -- "TODO" /workspace/project`
- the reusable configuration must explicitly exclude the repository's binary artifact types with grep options such as `--exclude=...`; relying only on `-I` or `--binary-files=without-match` is not sufficient for this repository
- the safe search must not print matches from binary files
- `TEST_RESULT` must be `SUCCESS` only if the configured search completes cleanly and only shows text-file matches

Notes:
- the repository intentionally contains both text files and binary files
- for this task, treat these six artifact files as the binary set to exclude:
  `/workspace/project/build/app.o`
  `/workspace/project/assets/logo.png`
  `/workspace/project/assets/icon.jpg`
  `/workspace/project/lib/libmath.a`
  `/workspace/project/dist/app.tar.gz`
  `/workspace/project/data/cache.dat`
- compiled objects, archives, images, and cache artifacts should be treated as binary files for this task even if a file-identification tool labels some of them as text-like content
- do not modify the repository contents under `/workspace/project`
