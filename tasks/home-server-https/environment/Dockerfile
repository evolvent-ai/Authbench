ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    ddclient \
    dnsutils \
    net-tools \
    nginx \
    openssl \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/www/html /solution /etc/ddclient /etc/ssl/homeserver

WORKDIR /app
ENV TEST_DIR=/tests
