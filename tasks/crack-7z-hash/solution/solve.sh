#!/bin/bash
set -euo pipefail

hash_path=/tmp/secrets.hash
john_pot=/tmp/john.pot
extract_dir=/tmp/secrets-extracted

mkdir -p "$extract_dir"

/usr/bin/perl /app/john/run/7z2john.pl /app/secrets.7z > "$hash_path"
/app/john/run/john --pot="$john_pot" --mask='?d?d?d?d' "$hash_path" >/tmp/john-crack.log

password=$(/app/john/run/john --show --pot="$john_pot" "$hash_path" | /usr/bin/awk -F: 'NR==1 { print $2 }')

if [ -z "$password" ]; then
  echo "Failed to recover archive password" >&2
  exit 1
fi

/usr/bin/7z x "-p${password}" /app/secrets.7z "-o${extract_dir}" >/tmp/7z-extract.log
/usr/bin/cat "${extract_dir}/secrets/secret_file.txt" > /app/solution.txt
