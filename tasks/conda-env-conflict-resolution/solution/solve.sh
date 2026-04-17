#!/bin/bash

set -euo pipefail

cd /app/project

cp environment.yml environment_original.yml

cat > environment.yml <<'EOF'
name: datasci
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy
  - scipy
  - pandas
  - tensorflow
  - pytorch
  - scikit-learn
  - transformers
EOF

conda env create --solver=libmamba -f environment.yml || conda env create -f environment.yml
conda run -n datasci python /app/project/test_imports.py
