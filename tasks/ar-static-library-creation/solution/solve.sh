#!/bin/bash
set -euo pipefail

cd /workspace/mathlib
./build.sh

test -s /workspace/solution.txt
