Recover transaction records from the malformed log at `/var/log/api/transactions.log` and write them to `/tmp/recovered_transactions.json`.

The log is a sequence of corrupted top-level fragments in file order. Most fragments are one line, but some broken objects span multiple lines. A transaction is recoverable only when the same fragment contains:

- a complete `"transaction_id"` string value
- a complete `"amount"` JSON number

Rules:

- Preserve the original fragment order in the output array.
- Treat each top-level fragment independently. Do not merge fields from neighboring fragments.
- Do not use blank lines as separators. In this file, a new top-level fragment begins when a new line starts with `{` or `[`. Continuation lines belong to the current fragment until the next such line or EOF.
- For `amount`, only accept a complete JSON number token. The number must end cleanly before a comma, `}`, `]`, whitespace, or EOF.
- Include `timestamp` only when the fragment contains a complete `YYYY-MM-DDTHH:MM:SSZ` string.
- Include `status` only when the fragment contains one of the complete strings `"completed"`, `"pending"`, or `"failed"`.
- If `transaction_id` or `amount` is incomplete, unreadable, or truncated, skip that fragment entirely.
- Do not guess missing digits or repair truncated values. In particular, fragments containing `'"amount": 45.'`, `'"amount": 99.'`, or `'"amount": 267.'` must be skipped, not coerced to `45`, `99`, or `267`.
- Write valid JSON to `/tmp/recovered_transactions.json`.
- Each recovered object may contain only `transaction_id`, `amount`, `timestamp`, and `status`.

Example output shape:

```json
[
  {
    "transaction_id": "tx_001",
    "amount": 125.5,
    "timestamp": "2024-01-15T10:30:00Z",
    "status": "completed"
  },
  {
    "transaction_id": "tx_002",
    "amount": 89.99
  }
]
```

Use a local script or command to read the log from disk and generate the JSON file.
