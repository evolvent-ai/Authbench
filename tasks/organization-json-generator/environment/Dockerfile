ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

COPY data /app/data
COPY schema.json /app/schema.json

RUN python3 -m pip install --no-cache-dir jsonschema

WORKDIR /app
ENV TEST_DIR=/tests
