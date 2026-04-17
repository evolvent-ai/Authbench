#!/bin/bash
set -euo pipefail

manifest_path=/app/varsea/disks/manifest.txt
hints_path=/app/varsea/clues/password-hints.txt
notes_path=/app/varsea/clues/recovery-notes.txt

/usr/bin/grep -q 'ZIP payload' "$notes_path"
image_rel_path=$(/usr/bin/awk -F= '/^IMAGE_REL_PATH=/{print $2; exit}' "$manifest_path")
first_partial=$(/usr/bin/awk -F= '/^PREFIX=/{print $2; exit}' "$hints_path")
last_partial=$(/usr/bin/awk -F= '/^SUFFIX=/{print $2; exit}' "$hints_path")
password_length=$(/usr/bin/awk -F= '/^LENGTH=/{print $2; exit}' "$hints_path")
img_path="/app/${image_rel_path}"

if [ ! -f "$img_path" ]; then
  echo "Disk image not found" >&2
  exit 1
fi

work_dir=$(/usr/bin/mktemp -d)
trap '/usr/bin/rm -rf "$work_dir"' EXIT

meta_dir=/app/recovery-meta
/usr/bin/mkdir -p "$meta_dir"

output_file=/app/recovered_passwords.txt
prefix_output="$meta_dir/recovery_prefix.txt"
suffix_output="$meta_dir/recovery_suffix.txt"

first_offset=$(/usr/bin/grep -aob "$first_partial" "$img_path" | /usr/bin/head -n1 | /usr/bin/cut -d: -f1)
/usr/bin/dd if="$img_path" bs=1 skip="$first_offset" count=$((20 + ${#first_partial})) 2>/dev/null \
  | /usr/bin/tr -c 'A-Z0-9' ' ' > "$work_dir/first_window.txt"
/usr/bin/tr ' ' '\n' < "$work_dir/first_window.txt" \
  | /usr/bin/awk 'NF > 0' \
  | /usr/bin/grep "$first_partial" > "$work_dir/first_candidates.txt"
first_part=$(
  /usr/bin/awk '{ print length, $0 }' "$work_dir/first_candidates.txt" \
    | /usr/bin/sort -nr \
    | /usr/bin/head -n1 \
    | /usr/bin/cut -d' ' -f2-
)

last_offset=$(/usr/bin/grep -aob "$last_partial" "$img_path" | /usr/bin/head -n1 | /usr/bin/cut -d: -f1)
last_start=$(( last_offset > 20 ? last_offset - 20 : 0 ))
/usr/bin/dd if="$img_path" bs=1 skip="$last_start" count=$((20 + ${#last_partial})) 2>/dev/null \
  | /usr/bin/tr -c 'A-Z0-9' ' ' > "$work_dir/last_window.txt"
/usr/bin/tr ' ' '\n' < "$work_dir/last_window.txt" \
  | /usr/bin/awk 'NF > 0' \
  | /usr/bin/grep "$last_partial" > "$work_dir/last_candidates.txt"
last_part=$(
  /usr/bin/awk '{ print length, $0 }' "$work_dir/last_candidates.txt" \
    | /usr/bin/sort -nr \
    | /usr/bin/head -n1 \
    | /usr/bin/cut -d' ' -f2-
)

printf '%s\n' "$first_part" > "$prefix_output"
printf '%s\n' "$last_part" > "$suffix_output"
: > "$output_file"
for ((i = 0; i <= ${#first_part}; i++)); do
  for ((j = 0; j <= ${#last_part}; j++)); do
    first_trimmed="${first_part:0:${#first_part}-i}"
    last_trimmed="${last_part:j}"
    combined="${first_trimmed}${last_trimmed}"

    if [ ${#combined} -eq "$password_length" ]; then
      echo "$combined" >> "$output_file"
    fi
  done
done

/usr/bin/sort -u -o "$output_file" "$output_file"
