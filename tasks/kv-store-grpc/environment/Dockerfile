ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

RUN python3 -m pip install --no-cache-dir \
      grpcio==1.73.0 \
      grpcio-tools==1.73.0 \
      pytest

WORKDIR /app
ENV TEST_DIR=/tests
