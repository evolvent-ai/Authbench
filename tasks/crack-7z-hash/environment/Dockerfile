ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    p7zip-full \
    perl \
    python3 \
    python3-pytest && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/john/run

WORKDIR /app

COPY task-deps/secrets.7z /app/secrets.7z
COPY john-run/7z2john.pl /app/john/run/7z2john.pl
COPY john-run/john /app/john/run/john

RUN chmod +x /app/john/run/7z2john.pl /app/john/run/john

ENV TEST_DIR=/tests
