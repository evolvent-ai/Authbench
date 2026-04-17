ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && apt-get install -y \
    git \
    python3-requests \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/python_project /solution /tmp/repo_main /tmp/repo_feature

COPY repo_main/ /tmp/repo_main/
COPY repo_feature/ /tmp/repo_feature/

RUN set -eux; \
    cp -r /tmp/repo_main/. /workspace/python_project/; \
    cd /workspace/python_project; \
    git init -b main; \
    git config user.email "bench@example.com"; \
    git config user.name "Terminal Bench"; \
    git add .; \
    git commit -m "Main branch baseline"; \
    git checkout -b feature-refactor; \
    find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +; \
    cp -r /tmp/repo_feature/. /workspace/python_project/; \
    git add -A; \
    git commit -m "Feature refactor changes"; \
    git checkout main

WORKDIR /workspace
ENV TEST_DIR=/tests
