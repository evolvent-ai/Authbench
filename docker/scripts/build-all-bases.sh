#!/usr/bin/env bash
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd -P)

"$ROOT_DIR/docker/scripts/build-base.sh" ubuntu-py
"$ROOT_DIR/docker/scripts/build-base.sh" python-py313
"$ROOT_DIR/docker/scripts/build-base.sh" python-py311
"$ROOT_DIR/docker/scripts/build-base.sh" tbench-ubuntu-py
"$ROOT_DIR/docker/scripts/build-base.sh" tbench-python-py313
"$ROOT_DIR/docker/scripts/build-base.sh" ubuntu-py-openclaw
"$ROOT_DIR/docker/scripts/build-base.sh" python-py313-openclaw
"$ROOT_DIR/docker/scripts/build-base.sh" python-py311-openclaw
"$ROOT_DIR/docker/scripts/build-base.sh" tbench-ubuntu-py-openclaw
"$ROOT_DIR/docker/scripts/build-base.sh" tbench-python-py313-openclaw
