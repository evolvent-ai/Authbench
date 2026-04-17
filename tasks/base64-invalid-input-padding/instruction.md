Repair padding-only corruption in the base64 payloads stored in `/var/log/api/requests.log`.

Each line in the log has this format:

```text
timestamp|endpoint|base64_payload
```

Some payloads have missing or extra `=` padding. Valid payloads decode to JSON objects.

Write `/tmp/repaired_payloads.txt` with one repaired entry per line:

```text
<original_base64>|<repaired_base64>
```

Requirements:

- process entries in their original order
- only include entries whose original payload is invalid under strict standard base64 decoding and JSON parsing
- do not change any non-padding characters
- every repaired payload must decode to valid JSON
- repair each invalid payload with this exact normalization rule:
  - strip all trailing `=` characters
  - append the minimum number of `=` characters needed to make the stripped payload length a multiple of 4
- this normalization may produce repaired payloads with `0`, `1`, or `2` trailing `=`

Examples of the required normalization rule:

```text
abc=== -> abc=
abcd=== -> abcd
abc -> abc=
ab -> ab==
```
