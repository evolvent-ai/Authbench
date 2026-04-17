#!/bin/bash

set -euo pipefail

cd /home/pyproject

cat > Makefile <<'EOF'
.PHONY: test

include config/python.mk
include config/testing.mk
include config/packaging.mk

test:
	$(PYTHON) -m pytest $(TEST_DIR)
EOF

make test

cat > /tmp/build_fix.txt <<'EOF'
status=fixed
approach=modified
EOF
