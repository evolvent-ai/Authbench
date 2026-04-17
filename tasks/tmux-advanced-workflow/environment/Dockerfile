ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

RUN apt-get update && apt-get install -y --no-install-recommends tmux git vim procps \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pytest==8.4.1

COPY resources/setup.sh /app/setup.sh
RUN chmod +x /app/setup.sh && /app/setup.sh

ENV TEST_DIR=/tests
