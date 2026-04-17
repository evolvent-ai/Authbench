ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends build-essential binutils file; \
    rm -rf /var/lib/apt/lists/*

COPY sensor.c /workspace/sensor_lib/sensor.c
COPY sensor.h /workspace/sensor_lib/sensor.h
COPY Makefile /workspace/sensor_lib/Makefile

WORKDIR /workspace
ENV TEST_DIR=/tests
