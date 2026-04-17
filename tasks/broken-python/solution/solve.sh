#!/bin/bash
set -euo pipefail

rm -rf /usr/local/lib/python3.13/site-packages/pip-*.dist-info \
  /usr/local/lib/python3.13/site-packages/setuptools-*.dist-info \
  /usr/local/lib/python3.13/site-packages/wheel-*.dist-info

python -m ensurepip --upgrade
