#!/bin/bash
set -euo pipefail

mkdir -p /app/recovered

find /app/sensitive_data -maxdepth 1 -type f -name '*.b64_content' -print0 | while IFS= read -r -d '' obfuscated_file; do
    encoded_name=$(basename "$obfuscated_file" .b64_content)
    original_name=$(printf '%s' "$encoded_name" | base64 -d)
    base64 -d "$obfuscated_file" > "/app/recovered/$original_name"
done
