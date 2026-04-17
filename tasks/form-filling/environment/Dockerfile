ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

RUN python3 -m pip install --no-cache-dir pypdf==5.6.1 scikit-learn==1.7.0

COPY documents /app/documents
COPY create_fillable_form.py /tmp/create_fillable_form.py

RUN python3 /tmp/create_fillable_form.py /app/fillable_form.pdf \
    && rm /tmp/create_fillable_form.py

WORKDIR /app
ENV TEST_DIR=/tests
