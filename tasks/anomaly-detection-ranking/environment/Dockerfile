ARG AUTHBENCH_UBUNTU_PY_PLAIN_BASE=authbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_UBUNTU_PY_PLAIN_BASE}

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-numpy \
    python3-pandas \
    && rm -rf /var/lib/apt/lists/*

COPY data /app/data
