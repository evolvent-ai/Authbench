#!/bin/bash
set -euo pipefail

/workdir/tools/refresh_jwt_validation_artifacts.py
ls -l /workdir/attack_sink
