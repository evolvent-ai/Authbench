ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && apt-get install -y python3-pytest && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/log/audit /home/agent

COPY data/audit.log /var/log/audit/audit.log

WORKDIR /app
ENV TEST_DIR=/tests
