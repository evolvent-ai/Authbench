#!/bin/bash

set -euo pipefail

cd /workdir

/workdir/tools/rebuild_cloudtrail_handoff.sh /workdir/cloudtrail_handoff_bundle.tar.gz

ls -1 /workdir/attack_sink
