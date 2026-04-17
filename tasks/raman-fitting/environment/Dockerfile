ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

WORKDIR /app
COPY graphene.dat /app/graphene.dat

RUN pip install scipy==1.16.0 numpy==2.3.1 pytest==8.4.1

ENV TEST_DIR=/tests
