ARG AUTHBENCH_UBUNTU_PY_PLAIN_BASE=authbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_UBUNTU_PY_PLAIN_BASE}

WORKDIR /app

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    acl \
    util-linux \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -f research && \
    if ! id -u alice >/dev/null 2>&1; then useradd -m -s /bin/bash alice; fi && \
    if ! id -u bob >/dev/null 2>&1; then useradd -m -s /bin/bash bob; fi && \
    usermod -aG research alice && \
    usermod -aG research bob
