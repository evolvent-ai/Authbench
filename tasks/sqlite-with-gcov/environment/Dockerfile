ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      jimsh \
      make \
      tcl \
      wget && \
    rm -rf /var/lib/apt/lists/*

RUN wget -O /tmp/sqlite.tar.gz https://www.sqlite.org/2024/sqlite-autoconf-3460100.tar.gz && \
    mkdir -p /app/sqlite && \
    tar -xzf /tmp/sqlite.tar.gz --strip-components=1 -C /app/sqlite && \
    rm -f /tmp/sqlite.tar.gz

WORKDIR /app
ENV TEST_DIR=/tests
