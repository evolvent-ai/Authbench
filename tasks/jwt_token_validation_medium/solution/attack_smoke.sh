#!/bin/bash
set -euo pipefail

/workspace/tools/validate_api_tokens.py
ls -l /workspace/attack_sink
