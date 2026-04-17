ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

COPY filesystem_spec /app/filesystem_spec

RUN python3 -m pip install --no-cache-dir \
      pytest-asyncio \
      pytest-mock

RUN printf '__version__ = "0+authbench"\n' > /app/filesystem_spec/fsspec/_version.py

WORKDIR /app/filesystem_spec
ENV TEST_DIR=/tests
ENV PYTHONPATH=/app/filesystem_spec
