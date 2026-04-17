ARG AUTHBENCH_PYTHON_PY311_PLAIN_BASE=authbench-python-py311-plain-base:local

FROM ${AUTHBENCH_PYTHON_PY311_PLAIN_BASE}

WORKDIR /app

RUN pip install --no-cache-dir --break-system-packages \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    httpx==0.25.2

COPY worker_queue.py /app/worker_queue.py

EXPOSE 8000

CMD ["tail", "-f", "/dev/null"]
