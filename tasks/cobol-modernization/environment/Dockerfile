ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y gnucobol3 && \
    rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python3 -m pip install --no-cache-dir pytest==8.4.1

WORKDIR /app

COPY src /app/src
COPY data /app/data
