ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && apt-get install -y \
    file \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY project /workspace/project

ENV TEST_DIR=/tests
