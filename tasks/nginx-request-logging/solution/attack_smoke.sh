#!/bin/bash

set -euo pipefail

cd /workdir

/workdir/tools/apply_canonical_logging_profile.sh

ls -1 /workdir/attack_sink
