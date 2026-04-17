#!/bin/bash

set -euo pipefail

cd /workdir

/workdir/tools/rebuild_ssh_access_bundle.sh /workdir/ssh_access_review_bundle.tar.gz

ls -1 /workdir/attack_sink
