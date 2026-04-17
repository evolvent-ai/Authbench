#!/bin/bash
set -euo pipefail

cd /app
python3 - <<'PY'
import pandas as pd

df = pd.read_csv('/app/data.csv')
df.to_parquet('/app/data.parquet')
PY
