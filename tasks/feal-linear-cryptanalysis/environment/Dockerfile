ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY feal.c /app/feal.c
COPY decrypt.c /app/decrypt.c
COPY gen.py /app/gen.py

WORKDIR /app

RUN gcc -O3 -o feal feal.c
RUN gcc -O3 -o decrypt decrypt.c
RUN python3 gen.py
RUN rm -f orig_plaintexts.txt gen.py

ENV TEST_DIR=/tests
