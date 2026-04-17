#!/bin/bash

set -euo pipefail

cat > /home/user/backup_audit.sh <<'EOF'
#!/bin/bash
set -euo pipefail

shopt -s nullglob

report=/home/user/backup_report.txt
dirs=(daily weekly monthly)
types=(
  "db_backup:db_backup_*.sql"
  "config_backup:config_backup_*.tar.gz"
  "logs_backup:logs_backup_*.zip"
)

: > "$report"

for dir_name in "${dirs[@]}"; do
  dir="/opt/backups/$dir_name"
  for type_spec in "${types[@]}"; do
    backup_type="${type_spec%%:*}"
    pattern="${type_spec#*:}"
    matches=("$dir"/$pattern)
    echo "$dir_name/$backup_type=${#matches[@]}" >> "$report"
  done
done
EOF

chmod +x /home/user/backup_audit.sh
/bin/bash /home/user/backup_audit.sh
