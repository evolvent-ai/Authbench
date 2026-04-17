#!/bin/bash
set -euo pipefail

TMPDIR=/tmp rustc /app/reference_compressor.rs -O -o /tmp/reference_compressor_bin
/tmp/reference_compressor_bin < /app/data.txt > /app/data.comp
test "$(/app/decomp < /app/data.comp)" = "$(< /app/data.txt)"
