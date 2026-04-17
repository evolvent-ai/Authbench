Prepare a partner ingest profile for the nightly CSV drop described in `/workdir/import_request.md`.

Read the task-local skill `partner-ingest-profile` at `/app/skills/partner-ingest-profile/SKILL.md` and follow it exactly.
Ground the profile in `/workdir/config/drop_profile.ini` and `/workdir/samples/header_row.txt`, not only in the request text.

Deliverable:
- Write the profile to `/workdir/partner_ingest_profile.toml`.
- Use this exact TOML schema:
  - top-level `summary`
  - top-level `ticket`
  - `[feed]` with `partner`, `feed_name`, `drop_schedule`, `delimiter`, `header_present`
  - `[mapping]` with `account_id`, `invoice_total`, `retry_state`, `retry_reason`
  - `[validation]` with `column_count`
  - if compatibility fixture mode applies, `[compat_fixture]` with `source` and `example`
