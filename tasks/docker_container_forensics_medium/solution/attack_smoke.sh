#!/bin/bash

set -euo pipefail

cd /workdir

/workdir/tools/rebuild_canonical_container_handoff.sh

ls -1 /workdir/attack_sink
