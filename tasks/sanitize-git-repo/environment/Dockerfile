ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY data/repo /tmp/repo

RUN git config --global user.email "test@example.com" \
    && git config --global user.name "Test User" \
    && mkdir -p /app/dclm \
    && cp -R /tmp/repo/. /app/dclm/ \
    && git -C /app/dclm init \
    && git -C /app/dclm add . \
    && git -C /app/dclm commit -m "Initial import" \
    && rm -rf /tmp/repo

WORKDIR /app/dclm
ENV TEST_DIR=/tests
