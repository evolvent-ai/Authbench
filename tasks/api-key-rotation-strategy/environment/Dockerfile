ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

WORKDIR /opt/auth

RUN mkdir -p /opt/auth

COPY config/config.ini /opt/auth/config.ini
COPY data/keys.json /opt/auth/keys.json
COPY check_key.py /opt/auth/check_key.py

ENV TEST_DIR=/tests
