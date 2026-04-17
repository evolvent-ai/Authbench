ARG AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE=authbench-tbench-python-py313-plain-base:local

FROM ${AUTHBENCH_TBENCH_PYTHON_PY313_PLAIN_BASE}

RUN python3 -m pip install --no-cache-dir pandas==2.3.0 numpy==2.3.1 pytest==8.4.1

COPY daily_temp_sf_high.csv /app/daily_temp_sf_high.csv
COPY daily_temp_sf_low.csv /app/daily_temp_sf_low.csv

WORKDIR /app
ENV TEST_DIR=/tests
