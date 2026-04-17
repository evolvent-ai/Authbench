ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

RUN /usr/local/bin/python3 -m pip install --no-cache-dir numpy==2.2.6 pytest==8.4.1

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY cross_entropy_method /app/cross_entropy_method
