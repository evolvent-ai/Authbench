ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /opt/monitor /workspace/data

COPY opt/monitor/process_logs.sh /opt/monitor/process_logs.sh
COPY data/server_valid.log /workspace/data/server_valid.log
COPY data/server_corrupted.log /workspace/data/server_corrupted.log

RUN chmod +x /opt/monitor/process_logs.sh

WORKDIR /opt/monitor
ENV TEST_DIR=/tests
