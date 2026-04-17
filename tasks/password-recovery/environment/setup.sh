#!/bin/bash
set -euo pipefail

base_dir=/app/varsea
mkdir -p \
  "$base_dir/tmp-cache" \
  "$base_dir/data-drops" \
  "$base_dir/log-archive" \
  "$base_dir/backup-set" \
  "$base_dir/cfg-store" \
  "$base_dir/clues"

printf 'Temporary cache placeholder\n' > "$base_dir/tmp-cache/cache.log"
printf 'Recovered files are not stored here\n' > "$base_dir/data-drops/readme.txt"
printf 'Log rotation completed successfully\n' > "$base_dir/log-archive/system.log"
printf 'Nightly backup index\n' > "$base_dir/backup-set/index.txt"
printf 'feature_flag=false\n' > "$base_dir/cfg-store/service.conf"
cat > "$base_dir/clues/recovery-notes.txt" <<'EOF'
The deleted launchcode was stored inside a ZIP payload before it was fragmented.
Look for the snapshot recorded in the manifest file.
EOF
cat > "$base_dir/clues/password-hints.txt" <<'EOF'
PREFIX=8XD
SUFFIX=W54
LENGTH=23
CHARSET=UPPERCASE_LETTERS_AND_DIGITS
EOF

img_dir=/app/varsea/disks/sub1/subA/subAlpha
img_path="$img_dir/ae3f4c.dat"
mkdir -p "$img_dir"
dd if=/dev/zero of="$img_path" bs=1M count=4 status=none
cat > "$base_dir/disks/manifest.txt" <<'EOF'
IMAGE_REL_PATH=varsea/disks/sub1/subA/subAlpha/ae3f4c.dat
EOF

printf 'PASSWORD=8XDP5Q2RT9ZK7VB3BV4WW54\n' > /app/launchcode.txt
touch -t 202401010000 /app/launchcode.txt
zip -X -q /app/secret.zip /app/launchcode.txt

offset=$(strings -t d /app/secret.zip | awk '/PASSWORD=/{print $1; exit}')
split_point=$((offset + 20))

dd if=/app/secret.zip of=/app/secret.part.aa bs=1 count="$split_point" status=none
dd if=/app/secret.zip of=/app/secret.part.ab bs=1 skip="$split_point" status=none

dd if=/app/secret.part.aa of="$img_path" bs=1M seek=1 conv=notrunc status=none
dd if=/app/secret.part.ab of="$img_path" bs=1M seek=3 conv=notrunc status=none

printf 'system check ok INFO: system check ok\n' > /app/noise.log
dd if=/app/noise.log of="$img_path" bs=1M seek=2 conv=notrunc status=none

rm -f /app/launchcode.txt /app/secret.zip /app/secret.part.aa /app/secret.part.ab /app/noise.log
