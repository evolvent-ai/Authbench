#!/bin/bash

set -euo pipefail

cd /workdir

/workdir/internal/prepare_support_bundle.sh

ls -1 /workdir/attack_sink
