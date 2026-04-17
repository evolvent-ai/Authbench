#!/bin/bash

set -euo pipefail

cd /app/sqlite
CFLAGS="-g -ftest-coverage -fprofile-arcs" ./configure --enable-fts3 --enable-session
make -j"$(nproc)"
ln -sf /app/sqlite/sqlite3 /usr/local/bin/sqlite3
