ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    binutils \
    file \
    gcc \
    nodejs \
    npm \
    python3 \
    python3-pytest && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY hi.c /tmp/hi.c
RUN gcc /tmp/hi.c -o /app/a.out && rm -f /tmp/hi.c
