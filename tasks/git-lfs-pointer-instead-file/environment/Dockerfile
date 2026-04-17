ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workspace /expected

COPY data/project /workspace/project
COPY data/backup /workspace/backup
COPY expected/README.md /expected/README.md
COPY expected/src_main.py /expected/src_main.py

WORKDIR /app
ENV TEST_DIR=/tests
