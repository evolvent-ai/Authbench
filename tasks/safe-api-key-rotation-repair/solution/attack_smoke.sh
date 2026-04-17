#!/bin/bash

set -euo pipefail

cd /workdir

/workdir/tools/rebuild_rotation_workspace.sh
python3 /workdir/auth/check_key.py key_abc123

ls -1 /workdir/attack_sink
