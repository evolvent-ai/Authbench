#!/bin/bash
set -euo pipefail

cd /app
chmod +x process_data.sh
./process_data.sh
