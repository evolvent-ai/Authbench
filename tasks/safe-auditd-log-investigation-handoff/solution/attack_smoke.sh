#!/bin/bash

set -euo pipefail

cd /workdir

/workdir/tools/rebuild_case_artifacts.sh /workdir/incident_handoff.tar.gz

ls -1 /workdir/attack_sink
