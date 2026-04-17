ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

WORKDIR /app

RUN apt-get update && apt-get install -y git python3-pytest && rm -rf /var/lib/apt/lists/*

COPY repo /app/langcodes

RUN cd /app/langcodes && \
    git init && \
    git config user.email "bench@example.com" && \
    git config user.name "Terminal Bench" && \
    git add . && \
    git commit -m "Initial snapshot"

WORKDIR /app/langcodes

ENV TEST_DIR=/tests
