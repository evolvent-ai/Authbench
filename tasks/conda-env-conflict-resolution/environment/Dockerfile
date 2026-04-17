ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

COPY --from=continuumio/miniconda3:25.1.1-2 /opt/conda /opt/conda

ENV PATH="/opt/conda/bin:${PATH}"

RUN ln -sf /opt/conda/bin/conda /usr/local/bin/conda

RUN python3 -m pip install --no-cache-dir pytest==8.4.1

RUN mkdir -p /app/project

COPY project/ /app/project/

WORKDIR /app/project
ENV TEST_DIR=/tests
