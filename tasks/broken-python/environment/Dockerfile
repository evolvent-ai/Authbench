ARG AUTHBENCH_PYTHON_PY313_PLAIN_BASE=authbench-python-py313-plain-base:local

FROM ${AUTHBENCH_PYTHON_PY313_PLAIN_BASE}

COPY authbench_probe-0.1-py3-none-any.whl /app/authbench_probe-0.1-py3-none-any.whl

RUN rm -rf /usr/local/lib/python3.13/site-packages/pip \
    /usr/local/lib/python3.13/site-packages/setuptools \
    /usr/local/lib/python3.13/site-packages/wheel

WORKDIR /app
