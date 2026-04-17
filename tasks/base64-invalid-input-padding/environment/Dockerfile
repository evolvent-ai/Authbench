ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

WORKDIR /app

RUN mkdir -p /var/log/api

COPY data/requests.log /var/log/api/requests.log

ENV TEST_DIR=/tests

