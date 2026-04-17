ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        gcc \
        libc6-dev \
        make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV TEST_DIR=/tests
