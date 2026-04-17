# Experiments

This directory keeps stable entrypoints for the baseline AuthBench runs.
Each experiment folder now follows the same pattern: `params.env` plus `run.sh`,
first materialize a plan, then optionally run Harbor.

Current baseline experiment folders:

- `oracle/`: batch oracle run for source tasks
- `permission-gen/`: batch permission-generation run for `tasks_gen/`
- `replay-allowall/`: batch allow-all replay run for `tasks_replay/`
- `replay-required/`: batch required-permissions replay run for source tasks
- `replay-generated/`: batch generated-policy replay run from a permission-gen Harbor job
- `full/`: orchestrate the whole source -> permission-gen -> replay pipeline
- `permission-gen-generated-replay/`: preset wrapper for prepare + permission-gen + generated replay only

The `permission-gen-generated-replay/` preset reuses a shared prepared
`tasks_gen/` root by default and only re-syncs source tasks when
`PREPARE_TASKS=always` or the prepared root is missing/incomplete.

The `run.sh` scripts automatically source repo `.env` when it exists.
Edit the corresponding `params.env` before running.
Set `RUN_HARBOR=0` to only materialize plans and generated task roots.
The generated replay script clears its generated destination by default so reruns stay idempotent.
