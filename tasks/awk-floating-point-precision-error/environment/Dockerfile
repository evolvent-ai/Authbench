ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update \
    && apt-get install -y gawk \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace

COPY data/transactions.csv /workspace/transactions.csv
COPY process_transactions.awk /workspace/process_transactions.awk

WORKDIR /app
ENV TEST_DIR=/tests
