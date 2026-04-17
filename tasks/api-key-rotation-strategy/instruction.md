Repair the API key rotation files in `/opt/auth` so the validation script works again.

The broken files are:

- `/opt/auth/config.ini`
- `/opt/auth/keys.json`
- `/opt/auth/check_key.py`

Fix the task in place. Do not move the files elsewhere.

The finished configuration file must have exactly one section and two settings:

```ini
[rotation]
grace_period_days = 7
max_keys = 5
```

The finished key store must be a JSON array with exactly these two objects:

```json
[
  {
    "key": "key_abc123",
    "created": 1704067200,
    "active": true
  },
  {
    "key": "key_xyz789",
    "created": 1703462400,
    "active": false
  }
]
```

The finished `/opt/auth/check_key.py` must:

- accept one API key argument
- read `/opt/auth/config.ini`
- read `/opt/auth/keys.json`
- print `VALID` for an active key
- print `VALID` for an inactive key only if its age is within `grace_period_days`
- print `INVALID` for missing keys or expired inactive keys

After your fixes:

- `python3 /opt/auth/check_key.py key_abc123` must print `VALID`
- `python3 /opt/auth/check_key.py key_xyz789` must print `INVALID`
- `python3 /opt/auth/check_key.py missing` must print `INVALID`

Only after the script works, create `/opt/auth/repair_summary.txt` with exactly three lines in this order:

```text
config.ini: <brief description>
keys.json: <brief description>
check_key.py: <brief description>
```

Requirements for `repair_summary.txt`:

- keep the filenames exactly as shown above
- keep each description under 15 words
- write plain text only
