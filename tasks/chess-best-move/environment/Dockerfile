ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

ENV PIP_NO_CACHE_DIR=1

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip stockfish && \
    pip3 install pillow==11.2.1 numpy==2.2.6 python-chess==1.999 pytest --break-system-packages && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY make.py /app/
COPY get_best_move.py /app/
RUN python3 /app/make.py && rm /app/make.py
