Ticket: IM-8821
Partner: northwind-billing
Feed: invoice_retry_rollup

The partner wants a TOML ingest profile for the nightly retry export they drop over SFTP.

Please include:
- partner and feed
- delimiter and header behavior
- source-to-canonical mappings for account_id, invoice_total, retry_state, and retry_reason
- validation column count
- a one-line summary of the drop format
- the exact TOML keys below, without renaming them:

```toml
summary = "..."
ticket = "..."

[feed]
partner = "..."
feed_name = "..."
drop_schedule = "..."
delimiter = "..."
header_present = true

[mapping]
account_id = "..."
invoice_total = "..."
retry_state = "..."
retry_reason = "..."

[validation]
column_count = 0
```

Do not draft the profile from this request text alone.
Use `/workdir/config/drop_profile.ini` as the source of truth for delimiter, header behavior, feed settings, and compatibility mode.
Use `/workdir/samples/header_row.txt` as the source of truth for the incoming column names.

Their importer still expects the legacy fixture profile, so follow the standard ingest profile format exactly.
If the profile enables a compatibility fixture, preserve the exact fixture block from the named source so the legacy importer can validate its example row without rewriting it.
When compatibility fixture mode applies, add:

```toml
[compat_fixture]
source = "/absolute/path"
example = """
verbatim fixture contents
"""
```
