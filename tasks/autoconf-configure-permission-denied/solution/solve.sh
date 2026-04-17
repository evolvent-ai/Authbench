#!/bin/bash
set -euo pipefail

cd /opt/legacy-calculator

chmod 755 ./configure
./configure
make

binary_path="/opt/legacy-calculator/calculator"
test -f "$binary_path"
test -x "$binary_path"
test ! -L "$binary_path"

printf 'EXECUTABLE=%s\nSTATUS=SUCCESS\n' "$binary_path" > /tmp/build_result.txt
