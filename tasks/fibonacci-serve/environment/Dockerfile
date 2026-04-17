ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

RUN python3 -m pip install --no-cache-dir flask requests

WORKDIR /app
ENV TEST_DIR=/tests
