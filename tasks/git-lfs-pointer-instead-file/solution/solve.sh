#!/bin/bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import shutil


POINTER_SIGNATURE = "version https://git-lfs.github.com/spec/v1"
PROJECT_ROOT = Path("/workspace/project")
BACKUP_ROOT = Path("/workspace/backup")
RESULT_PATH = Path("/workspace/result.txt")


def is_pointer_file(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return handle.readline().strip() == POINTER_SIGNATURE
    except OSError:
        return False


pointer_paths: list[Path] = []
for candidate in sorted(PROJECT_ROOT.rglob("*")):
    if candidate.is_file() and is_pointer_file(candidate):
        pointer_paths.append(candidate.relative_to(PROJECT_ROOT))

restored = 0
failed = 0

for relative_path in pointer_paths:
    project_file = PROJECT_ROOT / relative_path
    backup_file = BACKUP_ROOT / relative_path
    if backup_file.is_file():
        shutil.copyfile(backup_file, project_file)
        restored += 1
    else:
        failed += 1

RESULT_PATH.write_text(
    f"FOUND={len(pointer_paths)}\n"
    f"RESTORED={restored}\n"
    f"FAILED={failed}\n",
    encoding="utf-8",
)
PY
