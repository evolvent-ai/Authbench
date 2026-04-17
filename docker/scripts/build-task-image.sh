#!/usr/bin/env bash
set -eu

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <image-tag> <task-dir>" >&2
  exit 1
fi

IMAGE_TAG=$1
TASK_DIR=$2
ROOT_DIR=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd -P)
# shellcheck source=./package-mirrors.sh
. "$ROOT_DIR/docker/scripts/package-mirrors.sh"
authbench_apply_default_package_mirrors
case "$TASK_DIR" in
  /*)
    ABS_TASK_DIR=$(CDPATH= cd -- "$TASK_DIR" && pwd -P)
    ;;
  *)
    ABS_TASK_DIR=$(CDPATH= cd -- "$ROOT_DIR/$TASK_DIR" && pwd -P)
    ;;
esac
TASK_DOCKERFILE="$ABS_TASK_DIR/environment/Dockerfile"
DOCKERFILE_TO_BUILD="$TASK_DOCKERFILE"
TEMP_DIR=""

cleanup() {
  if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
  fi
}

trap cleanup EXIT

set -- docker build

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

if [ -n "${AUTHBENCH_UBUNTU_APT_MIRROR:-}" ] \
  || [ -n "${AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR:-}" ] \
  || [ -n "${AUTHBENCH_DEBIAN_APT_MIRROR:-}" ] \
  || [ -n "${AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR:-}" ] \
  || [ -n "${PIP_INDEX_URL:-}" ] \
  || [ -n "${PIP_EXTRA_INDEX_URL:-}" ] \
  || [ -n "${PIP_TRUSTED_HOST:-}" ]; then
  TEMP_DIR=$(mktemp -d)
  DOCKERFILE_TO_BUILD="$TEMP_DIR/Dockerfile"
  NETWORK_SNIPPET=$(cat <<'EOF'
ARG AUTHBENCH_UBUNTU_APT_MIRROR
ARG AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR
ARG AUTHBENCH_DEBIAN_APT_MIRROR
ARG AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR
ARG PIP_INDEX_URL
ARG PIP_EXTRA_INDEX_URL
ARG PIP_TRUSTED_HOST

ENV PIP_INDEX_URL=${PIP_INDEX_URL} \
    PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL} \
    PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}

RUN set -eu; \
    ubuntu_mirror="${AUTHBENCH_UBUNTU_APT_MIRROR:-}"; \
    ubuntu_security_mirror="${AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR:-}"; \
    debian_mirror="${AUTHBENCH_DEBIAN_APT_MIRROR:-}"; \
    debian_security_mirror="${AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR:-}"; \
    if [ -n "$ubuntu_mirror" ] && [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \
        ubuntu_mirror="${ubuntu_mirror%/}"; \
        sed -i -E "s|URIs: https?://archive\\.ubuntu\\.com/ubuntu/?|URIs: ${ubuntu_mirror}|g" /etc/apt/sources.list.d/ubuntu.sources; \
    fi; \
    if [ -n "$ubuntu_security_mirror" ] && [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \
        ubuntu_security_mirror="${ubuntu_security_mirror%/}"; \
        sed -i -E "s|URIs: https?://security\\.ubuntu\\.com/ubuntu/?|URIs: ${ubuntu_security_mirror}|g" /etc/apt/sources.list.d/ubuntu.sources; \
    fi; \
    if [ -n "$debian_mirror" ] && [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        debian_mirror="${debian_mirror%/}"; \
        sed -i -E "s|URIs: https?://deb\\.debian\\.org/debian/?|URIs: ${debian_mirror}|g" /etc/apt/sources.list.d/debian.sources; \
    fi; \
    if [ -n "$debian_security_mirror" ] && [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        debian_security_mirror="${debian_security_mirror%/}"; \
        sed -i -E "s|URIs: https?://security\\.debian\\.org/debian-security/?|URIs: ${debian_security_mirror}|g" /etc/apt/sources.list.d/debian.sources; \
    fi
EOF
)
  awk -v snippet="$NETWORK_SNIPPET" '
    { print }
    !inserted && $1 == "FROM" {
      print ""
      print snippet
      inserted = 1
    }
  ' "$TASK_DOCKERFILE" > "$DOCKERFILE_TO_BUILD"
fi

"$@" -t "$IMAGE_TAG" -f "$DOCKERFILE_TO_BUILD" "$ABS_TASK_DIR/environment"
