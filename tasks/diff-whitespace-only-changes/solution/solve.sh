#!/bin/bash
set -euo pipefail

repo_dir=/workspace/python_project

mapfile -t changed_files < <(git -C "$repo_dir" diff --name-only main feature-refactor)

substantive_changes=()
whitespace_only=()

for file in "${changed_files[@]}"; do
    if git -C "$repo_dir" diff --ignore-all-space --quiet main feature-refactor -- "$file"; then
        whitespace_only+=("$file")
    else
        substantive_changes+=("$file")
    fi
done

{
    printf 'SUBSTANTIVE_CHANGES='
    (
        IFS=,
        printf '%s' "${substantive_changes[*]}"
    )
    printf '\n'
    printf 'WHITESPACE_ONLY='
    (
        IFS=,
        printf '%s' "${whitespace_only[*]}"
    )
    printf '\n'
} > /workspace/analysis_result.txt
