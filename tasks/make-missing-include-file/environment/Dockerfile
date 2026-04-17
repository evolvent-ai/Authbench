ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && apt-get install -y \
    make \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/pyproject/src /home/pyproject/tests /home/pyproject/config /home/pyproject/build /tmp

COPY Makefile /home/pyproject/Makefile
COPY config/python.mk /home/pyproject/config/python.mk
COPY config/testing.mk /home/pyproject/config/testing.mk
COPY config/packaging.mk /home/pyproject/config/packaging.mk
COPY src/calculator.py /home/pyproject/src/calculator.py
COPY tests/test_calculator.py /home/pyproject/tests/test_calculator.py

WORKDIR /home/pyproject
ENV TEST_DIR=/tests
