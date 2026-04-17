#!/bin/bash
set -euo pipefail

cd /app
python3 - <<'PY'
import pandas as pd

high = pd.read_csv('/app/daily_temp_sf_high.csv')
low = pd.read_csv('/app/daily_temp_sf_low.csv')

high['date'] = pd.to_datetime(high['date'], format='%Y-%m-%d')
low['date'] = low['date'].astype(str).str.replace('/', '-', regex=False)
low['date'] = pd.to_datetime(low['date'], format='%m-%d-%Y %H:%M:%S').dt.normalize()

merged = high.rename(columns={'temperature': 'temp_high'}).merge(
    low.rename(columns={'temperature': 'temp_low'}),
    how='inner',
    on=['date'],
)
merged['difference'] = merged['temp_high'] - merged['temp_low']

with open('/app/avg_temp.txt', 'w', encoding='utf-8') as f:
    f.write(str(merged['difference'].mean()))
PY
