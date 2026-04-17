#!/usr/bin/env bash
set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <ubuntu-py|python-py311|python-py313|tbench-ubuntu-py|tbench-python-py313|ubuntu-py-openclaw|python-py311-openclaw|python-py313-openclaw|tbench-ubuntu-py-openclaw|tbench-python-py313-openclaw>" >&2
  exit 1
fi

ROOT_DIR=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd -P)
TARGET=$1
GHCR_PREFIX=${AUTHBENCH_GHCR_MIRROR_PREFIX:-ghcr.io}
GHCR_PREFIX=${GHCR_PREFIX%/}
# shellcheck source=./package-mirrors.sh
. "$ROOT_DIR/docker/scripts/package-mirrors.sh"
authbench_apply_default_package_mirrors

case "$TARGET" in
  ubuntu-py|python-py311|python-py313|tbench-ubuntu-py|tbench-python-py313|ubuntu-py-openclaw|python-py311-openclaw|python-py313-openclaw|tbench-ubuntu-py-openclaw|tbench-python-py313-openclaw)
    set -- docker build
    ;;
  *)
    echo "Unknown base target: $TARGET" >&2
    exit 1
    ;;
esac

set -- "$@" --build-arg "AUTHBENCH_PYTHON_PY313_PLAIN_BASE=${AUTHBENCH_PYTHON_PY313_PLAIN_BASE:-authbench-python-py313-plain-base:local}"
set -- "$@" --build-arg "AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE:-authbench-tbench-python-py313-plain-base:local}"
set -- "$@" --build-arg "AUTHBENCH_PYTHON_PY311_PLAIN_BASE=${AUTHBENCH_PYTHON_PY311_PLAIN_BASE:-authbench-python-py311-plain-base:local}"
set -- "$@" --build-arg "AUTHBENCH_UBUNTU_PY_PLAIN_BASE=${AUTHBENCH_UBUNTU_PY_PLAIN_BASE:-authbench-ubuntu-py-plain-base:local}"
set -- "$@" --build-arg "AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE:-authbench-tbench-ubuntu-py-plain-base:local}"
set -- "$@" --build-arg "AUTHBENCH_PYTHON_PY313_OPENCLAW_BASE=${AUTHBENCH_PYTHON_PY313_OPENCLAW_BASE:-authbench-python-py313-openclaw-base:local}"
set -- "$@" --build-arg "AUTHBENCH_TBENCH_PYTHON_PY313_OPENCLAW_BASE=${AUTHBENCH_TBENCH_PYTHON_PY313_OPENCLAW_BASE:-authbench-tbench-python-py313-openclaw-base:local}"
set -- "$@" --build-arg "AUTHBENCH_PYTHON_PY311_OPENCLAW_BASE=${AUTHBENCH_PYTHON_PY311_OPENCLAW_BASE:-authbench-python-py311-openclaw-base:local}"
set -- "$@" --build-arg "AUTHBENCH_UBUNTU_PY_OPENCLAW_BASE=${AUTHBENCH_UBUNTU_PY_OPENCLAW_BASE:-authbench-ubuntu-py-openclaw-base:local}"
set -- "$@" --build-arg "AUTHBENCH_TBENCH_UBUNTU_PY_OPENCLAW_BASE=${AUTHBENCH_TBENCH_UBUNTU_PY_OPENCLAW_BASE:-authbench-tbench-ubuntu-py-openclaw-base:local}"
set -- "$@" --build-arg "AUTHBENCH_GHCR_PREFIX=${GHCR_PREFIX}"

if [ "${AUTHBENCH_FORWARD_BUILD_PROXY:-0}" = "1" ]; then
  if [ -n "${HTTP_PROXY:-}" ]; then
    set -- "$@" --build-arg "HTTP_PROXY=${HTTP_PROXY}"
  fi
  if [ -n "${HTTPS_PROXY:-}" ]; then
    set -- "$@" --build-arg "HTTPS_PROXY=${HTTPS_PROXY}"
  fi
  if [ -n "${NO_PROXY:-}" ]; then
    set -- "$@" --build-arg "NO_PROXY=${NO_PROXY}"
  fi
  if [ -n "${http_proxy:-}" ]; then
    set -- "$@" --build-arg "http_proxy=${http_proxy}"
  fi
  if [ -n "${https_proxy:-}" ]; then
    set -- "$@" --build-arg "https_proxy=${https_proxy}"
  fi
  if [ -n "${no_proxy:-}" ]; then
    set -- "$@" --build-arg "no_proxy=${no_proxy}"
  fi
fi
if [ -n "${AUTHBENCH_UBUNTU_APT_MIRROR:-}" ]; then
  set -- "$@" --build-arg "AUTHBENCH_UBUNTU_APT_MIRROR=${AUTHBENCH_UBUNTU_APT_MIRROR}"
fi
if [ -n "${AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR:-}" ]; then
  set -- "$@" --build-arg "AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR=${AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR}"
fi
if [ -n "${AUTHBENCH_DEBIAN_APT_MIRROR:-}" ]; then
  set -- "$@" --build-arg "AUTHBENCH_DEBIAN_APT_MIRROR=${AUTHBENCH_DEBIAN_APT_MIRROR}"
fi
if [ -n "${AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR:-}" ]; then
  set -- "$@" --build-arg "AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR=${AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR}"
fi
if [ -n "${PIP_INDEX_URL:-}" ]; then
  set -- "$@" --build-arg "PIP_INDEX_URL=${PIP_INDEX_URL}"
fi
if [ -n "${PIP_EXTRA_INDEX_URL:-}" ]; then
  set -- "$@" --build-arg "PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL}"
fi
if [ -n "${PIP_TRUSTED_HOST:-}" ]; then
  set -- "$@" --build-arg "PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}"
fi

case "$TARGET" in
  ubuntu-py)
    "$@" -t authbench-ubuntu-py-plain-base:local -f "$ROOT_DIR/docker/bases/ubuntu-py/plain.Dockerfile" "$ROOT_DIR"
    ;;
  python-py313)
    "$@" -t authbench-python-py313-plain-base:local -f "$ROOT_DIR/docker/bases/python-py313/plain.Dockerfile" "$ROOT_DIR"
    ;;
  tbench-python-py313)
    "$@" -t authbench-tbench-python-py313-plain-base:local -f "$ROOT_DIR/docker/bases/tbench-python-py313/plain.Dockerfile" "$ROOT_DIR"
    ;;
  python-py311)
    "$@" -t authbench-python-py311-plain-base:local -f "$ROOT_DIR/docker/bases/python-py311/plain.Dockerfile" "$ROOT_DIR"
    ;;
  ubuntu-py-openclaw)
    "$@" -t authbench-ubuntu-py-openclaw-base:local -f "$ROOT_DIR/docker/bases/ubuntu-py/openclaw.Dockerfile" "$ROOT_DIR"
    ;;
  tbench-ubuntu-py)
    "$@" -t authbench-tbench-ubuntu-py-plain-base:local -f "$ROOT_DIR/docker/bases/tbench-ubuntu-py/plain.Dockerfile" "$ROOT_DIR"
    ;;
  python-py313-openclaw)
    "$@" -t authbench-python-py313-openclaw-base:local -f "$ROOT_DIR/docker/bases/python-py313/openclaw.Dockerfile" "$ROOT_DIR"
    ;;
  tbench-python-py313-openclaw)
    "$@" -t authbench-tbench-python-py313-openclaw-base:local -f "$ROOT_DIR/docker/bases/tbench-python-py313/openclaw.Dockerfile" "$ROOT_DIR"
    ;;
  python-py311-openclaw)
    "$@" -t authbench-python-py311-openclaw-base:local -f "$ROOT_DIR/docker/bases/python-py311/openclaw.Dockerfile" "$ROOT_DIR"
    ;;
  tbench-ubuntu-py-openclaw)
    "$@" -t authbench-tbench-ubuntu-py-openclaw-base:local -f "$ROOT_DIR/docker/bases/tbench-ubuntu-py/openclaw.Dockerfile" "$ROOT_DIR"
    ;;
esac
