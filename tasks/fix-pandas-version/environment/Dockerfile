ARG AUTHBENCH_PYTHON_PY311_PLAIN_BASE=authbench-python-py311-plain-base:local

FROM ${AUTHBENCH_PYTHON_PY311_PLAIN_BASE}

RUN apt-get update && apt-get install -y --no-install-recommends tmux curl asciinema \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir \
    "pandas==1.5.3" \
    "numpy==1.24.4" \
    "pyarrow==12.0.1" \
    "packaging>=21.0" \
    "pytest==8.4.1"

COPY src/ /app/src/

ENV TEST_DIR=/tests
