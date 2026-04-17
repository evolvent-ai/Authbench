ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && apt-get install -y \
    bc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/data_processor /solution

COPY data/sample_data.csv /opt/data_processor/sample_data.csv
COPY opt/data_processor/process_records.sh /opt/data_processor/process_records.sh

RUN chmod +x /opt/data_processor/process_records.sh

WORKDIR /opt/data_processor
ENV TEST_DIR=/tests
