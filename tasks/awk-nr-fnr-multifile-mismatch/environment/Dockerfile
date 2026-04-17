ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update \
    && apt-get install -y gawk \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /data/sales /scripts /expected /solution

COPY data /data
COPY scripts /scripts
COPY expected /expected

WORKDIR /app
ENV TEST_DIR=/tests
