ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/project/src

RUN bash <<'EOF'
set -euo pipefail

cd /workspace/project
git init -b main
git config user.name "Developer User"
git config user.email "dev@example.com"

cat > README.md <<'TEXT'
# Project

This is a sample project for testing git recovery operations.
TEXT

cat > src/main.py <<'TEXT'
def bootstrap():
    return "service starting"
TEXT

git add README.md src/main.py
GIT_AUTHOR_DATE="2023-11-13T10:00:00-0500" GIT_COMMITTER_DATE="2023-11-13T10:00:00-0500" git commit -m "Initial commit"

cat > src/auth.py <<'TEXT'
def register(username):
    return f"registered:{username}"
TEXT

git add src/auth.py
GIT_AUTHOR_DATE="2023-11-13T11:00:00-0500" GIT_COMMITTER_DATE="2023-11-13T11:00:00-0500" git commit -m "Add user registration feature"

cat > src/models.py <<'TEXT'
USERS_TABLE = "users"
TEXT

git add src/models.py
GIT_AUTHOR_DATE="2023-11-13T12:00:00-0500" GIT_COMMITTER_DATE="2023-11-13T12:00:00-0500" git commit -m "Add database models"

cat > src/main.py <<'TEXT'
def login(username, password):
    if not username or not password:
        return {"status": "error", "message": "missing credentials"}
    return {"status": "ok", "user": username}
TEXT

git add src/main.py
GIT_AUTHOR_DATE="2023-11-13T13:00:00-0500" GIT_COMMITTER_DATE="2023-11-13T13:00:00-0500" git commit -m "Implement login endpoint"

printf "%s\n" "$(git rev-parse main)" > /workspace/original_main_sha.txt

git checkout --detach HEAD~2

cat > src/auth.py <<'TEXT'
def register(username):
    cleaned = username.strip()
    if not cleaned:
        raise ValueError("username is required")
    return f"registered:{cleaned}"
TEXT

git add src/auth.py
GIT_AUTHOR_DATE="2023-11-13T14:00:00-0500" GIT_COMMITTER_DATE="2023-11-13T14:00:00-0500" git commit -m "Fix bug in authentication"

cat > src/validation.py <<'TEXT'
def validate_username(username):
    return bool(username and username.strip())
TEXT

git add src/validation.py
GIT_AUTHOR_DATE="2023-11-13T15:00:00-0500" GIT_COMMITTER_DATE="2023-11-13T15:00:00-0500" git commit -m "Add validation logic"

cat > src/main.py <<'TEXT'
from auth import register
from validation import validate_username


def safe_register(username):
    if not validate_username(username):
        return {"status": "error", "message": "invalid username"}
    try:
        return {"status": "ok", "result": register(username)}
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}
TEXT

git add src/main.py
GIT_AUTHOR_DATE="2023-11-13T16:00:00-0500" GIT_COMMITTER_DATE="2023-11-13T16:00:00-0500" git commit -m "Update error handling"

git status --short
EOF

WORKDIR /workspace
ENV TEST_DIR=/tests
