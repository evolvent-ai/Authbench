#!/bin/bash
set -euo pipefail

PROJECT_ROOT=/workspace/project
CONFIG_FILE=/workspace/grep-safe.conf
OUTPUT_FILE=/tmp/grep-todo-output.txt

cat > "$CONFIG_FILE" <<'EOF'
--binary-files=without-match
--exclude=*.o
--exclude=*.png
--exclude=*.jpg
--exclude=*.a
--exclude=*.tar.gz
--exclude=*.dat
EOF

BINARY_COUNT="$(
  find "$PROJECT_ROOT" -type f \
    \( -name '*.o' -o -name '*.png' -o -name '*.jpg' -o -name '*.a' -o -name '*.tar.gz' -o -name '*.dat' \) \
    | wc -l | tr -d ' '
)"

mapfile -t GREP_OPTIONS < "$CONFIG_FILE"

grep "${GREP_OPTIONS[@]}" -r -- "TODO" "$PROJECT_ROOT" > "$OUTPUT_FILE"

if grep -Eq 'app\.o|logo\.png|icon\.jpg|libmath\.a|app\.tar\.gz|cache\.dat' "$OUTPUT_FILE"; then
  TEST_RESULT=FAILURE
else
  TEST_RESULT=SUCCESS
fi

cat > /workspace/solution.txt <<EOF
BINARY_COUNT=${BINARY_COUNT}
CONFIG_FILE=${CONFIG_FILE}
TEST_RESULT=${TEST_RESULT}
EOF
