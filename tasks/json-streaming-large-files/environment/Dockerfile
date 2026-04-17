ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && apt-get install -y python3-pytest && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/data /workspace/output

COPY data/user_activity.json /workspace/data/user_activity.json

WORKDIR /workspace
ENV TEST_DIR=/tests
