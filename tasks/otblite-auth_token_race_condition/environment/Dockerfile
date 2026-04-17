ARG AUTHBENCH_PYTHON_PY311_PLAIN_BASE=authbench-python-py311-plain-base:local

FROM ${AUTHBENCH_PYTHON_PY311_PLAIN_BASE}

WORKDIR /workspace
RUN ln -s /workspace /app

# Copy requirements and install dependencies
COPY requirements.txt /workspace/
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Copy application code (with the buggy token_service.py)
COPY auth_gateway/ /workspace/auth_gateway/

# Copy startup scripts
COPY start_redis.sh /workspace/
COPY start_gateway.sh /workspace/
COPY start.sh /workspace/

RUN chmod +x /workspace/start_redis.sh /workspace/start_gateway.sh /workspace/start.sh

# Keep container running - test.sh will start services
CMD ["tail", "-f", "/dev/null"]
