ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

WORKDIR /app

RUN mkdir -p /app/sensitive_data /app/recovered

COPY NOTE_FROM_ATTACKER.txt /app/NOTE_FROM_ATTACKER.txt
COPY setup_files/ /app/sensitive_data/

ENV TEST_DIR=/tests
