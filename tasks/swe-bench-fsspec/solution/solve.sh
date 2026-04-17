#!/bin/bash

set -euo pipefail

python3 - <<'PY'
from pathlib import Path


path = Path("/app/filesystem_spec/fsspec/implementations/dirfs.py")
text = path.read_text()

if "async def open_async(" not in text:
    text = text.rstrip() + """

    async def open_async(
        self,
        path,
        *args,
        **kwargs,
    ):
        return await self.fs.open_async(
            self._join(path),
            *args,
            **kwargs,
        )
"""
    path.write_text(text + "\n")
PY
