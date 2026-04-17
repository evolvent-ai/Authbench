ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && \
    apt-get install -y jq python3-pytest && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/log/api /tmp

COPY data/transactions.log /var/log/api/transactions.log

WORKDIR /workspace
ENV TEST_DIR=/tests
