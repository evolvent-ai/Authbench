ARG AUTHBENCH_PYTHON_PY311_PLAIN_BASE=authbench-python-py311-plain-base:local

FROM ${AUTHBENCH_PYTHON_PY311_PLAIN_BASE}

WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
