ARG AUTHBENCH_PYTHON_PY311_PLAIN_BASE=authbench-python-py311-plain-base:local

FROM ${AUTHBENCH_PYTHON_PY311_PLAIN_BASE}

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ca-certificates && \
    python3 -m pip install --no-cache-dir numpy==1.23.4 && \
    rm -rf /var/lib/apt/lists/*

COPY repo /app/astropy

WORKDIR /app/astropy
ENV TEST_DIR=/tests
