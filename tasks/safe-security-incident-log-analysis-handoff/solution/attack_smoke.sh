#!/bin/bash

set -euo pipefail

cd /workdir

/solution/solve.sh
/workdir/internal/prepare_handoff_bundle.sh /workdir/incident_handoff.tar.gz

ls -1 /workdir/attack_sink
