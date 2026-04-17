#!/bin/bash
set -euo pipefail

cat > /app/convert.py << 'EOF'
with open("/app/graphene.dat", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    line = line.strip().replace(",", ".").replace("\t", ",")
    new_lines.append(line)

with open("/app/graphene_format.dat", "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(new_lines))
EOF

python3 /app/convert.py

cat > /app/fit.py << 'EOF'
import json

import numpy as np
from scipy.optimize import curve_fit


def lorentzian(x, x0, gamma, amplitude, offset):
    return amplitude * (gamma**2) / ((x - x0) ** 2 + gamma**2) + offset


def fit_lorentzian(x, y, x0_guess, gamma_guess):
    amplitude_guess = np.max(y) - np.min(y)
    offset_guess = np.min(y)
    p0 = [x0_guess, gamma_guess, amplitude_guess, offset_guess]
    params, _ = curve_fit(lorentzian, x, y, p0=p0)
    return params


data = np.loadtxt("/app/graphene_format.dat", delimiter=",").T
x = data[0]
y = data[1]
x = 1e7 / x

mask_g = (x > 1500) & (x < 1700)
mask_2d = (x > 2500) & (x < 2900)

params_g = fit_lorentzian(x[mask_g], y[mask_g], x0_guess=1580, gamma_guess=10)
params_2d = fit_lorentzian(x[mask_2d], y[mask_2d], x0_guess=2700, gamma_guess=10)

x0_g, gamma_g, amplitude_g, offset_g = params_g
x0_2d, gamma_2d, amplitude_2d, offset_2d = params_2d

with open("/app/results.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "G": {
                "x0": float(x0_g),
                "gamma": float(gamma_g),
                "amplitude": float(amplitude_g),
                "offset": float(offset_g),
            },
            "2D": {
                "x0": float(x0_2d),
                "gamma": float(gamma_2d),
                "amplitude": float(amplitude_2d),
                "offset": float(offset_2d),
            },
        },
        f,
        indent=2,
    )
EOF

python3 /app/fit.py
