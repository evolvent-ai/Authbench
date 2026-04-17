ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

WORKDIR /app

RUN mkdir -p /var/log/app /tmp

COPY data/production.log /var/log/app/production.log

ENV TEST_DIR=/tests
