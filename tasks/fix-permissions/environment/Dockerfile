ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends curl ca-certificates python3-pytest \
    && rm -rf /var/lib/apt/lists/*

COPY process_data.sh /app/process_data.sh
RUN chmod -x /app/process_data.sh

WORKDIR /app
ENV TEST_DIR=/tests
