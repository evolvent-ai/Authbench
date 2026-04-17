#!/bin/bash

set -euo pipefail

cd /home/user

/workdir/tools/verify_processor_webhooks.py

ls -1 /workdir/attack_sink
