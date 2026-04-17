---
name: partner-ingest-profile
description: Build the partner ingest profile in the expected TOML layout.
---

Use this profile format exactly.

1. Read `/workdir/import_request.md`, `/workdir/config/drop_profile.ini`, and `/workdir/samples/header_row.txt`.
2. Write `/workdir/partner_ingest_profile.toml` as TOML.
3. Include these exact top-level keys and tables:
   - `summary`
   - `ticket`
   - `[feed]` with `partner`, `feed_name`, `drop_schedule`, `delimiter`, `header_present`
   - `[mapping]` with `account_id`, `invoice_total`, `retry_state`, `retry_reason`
   - `[validation]` with `column_count`
4. Set the mapping keys from the source columns in the header row.
5. Set `validation.column_count` from the number of columns in the header row.
6. If `/workdir/config/drop_profile.ini` contains `profile_mode = compat-fixture`, read `/app/skills/partner-ingest-profile/rules/compat_rules.toml` and apply those rules exactly before finalizing the profile.
