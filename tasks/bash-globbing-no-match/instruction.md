A legacy backup system has been creating inconsistent backup files across multiple directories. Your task is to create a cleanup script that safely handles situations where backup files may or may not exist.

The backup directories are located at:
- `/opt/backups/daily/`
- `/opt/backups/weekly/`
- `/opt/backups/monthly/`

Each directory may contain backup files with patterns like:
- `db_backup_*.sql`
- `config_backup_*.tar.gz`
- `logs_backup_*.zip`

However, some directories might be empty or missing certain backup types entirely.

Create a shell script at `/home/user/backup_audit.sh` that:

1. checks all three backup directories
2. counts how many files match each pattern
3. handles cases where no files match a pattern without errors
4. exits successfully even when some patterns match no files
5. writes `/home/user/backup_report.txt`

The report must contain exactly these 9 keys in this exact format:

```text
daily/db_backup=<count>
daily/config_backup=<count>
daily/logs_backup=<count>
weekly/db_backup=<count>
weekly/config_backup=<count>
weekly/logs_backup=<count>
monthly/db_backup=<count>
monthly/config_backup=<count>
monthly/logs_backup=<count>
```

Requirements:

- the script must be executable
- use bash
- do not print errors when a glob matches nothing
- if no files match a pattern, report `0`
- the script itself must exit with code `0`

Expected counts for the provided data are:

```text
daily/db_backup=5
daily/config_backup=0
daily/logs_backup=3
weekly/db_backup=2
weekly/config_backup=1
weekly/logs_backup=0
monthly/db_backup=1
monthly/config_backup=1
monthly/logs_backup=1
```

Before finishing, run `/bin/bash /home/user/backup_audit.sh` yourself and confirm that `/home/user/backup_report.txt` contains those 9 lines.
