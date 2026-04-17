ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        gcc \
        rustc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY decomp.c /app/decomp.c
RUN gcc -O3 /app/decomp.c -o /app/decomp
COPY data.txt /app/data.txt
COPY reference_compressor.rs /app/reference_compressor.rs

ENV TEST_DIR=/tests
