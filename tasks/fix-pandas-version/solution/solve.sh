#!/bin/bash
set -euo pipefail

cd /app
pip install --no-cache-dir pandas==2.0.0 pyarrow==14.0.0
python -c "import pandas as pd; print(pd.__version__)"
