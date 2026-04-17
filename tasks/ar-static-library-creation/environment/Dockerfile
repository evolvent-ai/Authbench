ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends build-essential binutils; \
    rm -rf /var/lib/apt/lists/*

COPY mathlib /workspace/mathlib

RUN chmod +x /workspace/mathlib/build.sh

WORKDIR /workspace
ENV TEST_DIR=/tests
