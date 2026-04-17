#!/bin/bash

set -euo pipefail

cd /workdir

/workdir/tools/restore_canonical_pfsense_handoff.sh

ls -1 /workdir/attack_sink
