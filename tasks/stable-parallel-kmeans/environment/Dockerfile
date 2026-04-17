ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

RUN /usr/local/bin/python3 -m pip install --no-cache-dir \
    joblib==1.5.1 \
    numpy==2.3.1 \
    pytest==8.4.1 \
    scikit-learn==1.7.0

WORKDIR /app
