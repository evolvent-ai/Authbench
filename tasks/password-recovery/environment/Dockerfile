ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    binutils \
    python3 \
    python3-pytest \
    zip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY setup.sh /tmp/password-recovery-setup.sh
RUN bash /tmp/password-recovery-setup.sh && rm -f /tmp/password-recovery-setup.sh

ENV TEST_DIR=/tests
