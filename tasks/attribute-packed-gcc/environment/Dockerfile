ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends build-essential python3-pytest; \
    rm -rf /var/lib/apt/lists/*

COPY packet_parser.c /workspace/packet_parser.c
COPY data/test_packet.bin /workspace/test_packet.bin

WORKDIR /workspace
ENV TEST_DIR=/tests
