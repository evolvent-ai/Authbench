ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/calculator

RUN bash <<'EOF'
set -euo pipefail

cd /workspace/calculator
git init -b main
git config user.name "Developer User"
git config user.email "dev@example.com"

cat > calculator.py <<'PY'
#!/usr/bin/env python3


class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b


if __name__ == "__main__":
    calc = Calculator()
    print("Calculator Test:")
    print(f"5 + 3 = {calc.add(5, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
PY

chmod +x calculator.py
git add calculator.py
GIT_AUTHOR_DATE="2024-01-10T09:00:00+0000" GIT_COMMITTER_DATE="2024-01-10T09:00:00+0000" git commit -m "Initial calculator implementation"

git checkout -b feature-advanced-ops
cat > calculator.py <<'PY'
#!/usr/bin/env python3


class Calculator:
    def add(self, a, b):
        result = a + b
        return result

    def subtract(self, a, b):
        result = a - b
        return result

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


if __name__ == "__main__":
    calc = Calculator()
    print("Calculator Test:")
    print(f"5 + 3 = {calc.add(5, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
    print(f"6 * 7 = {calc.multiply(6, 7)}")
    print(f"15 / 3 = {calc.divide(15, 3)}")
PY

chmod +x calculator.py
git add calculator.py
GIT_AUTHOR_DATE="2024-01-10T10:00:00+0000" GIT_COMMITTER_DATE="2024-01-10T10:00:00+0000" git commit -m "Add multiply and divide operations"

git checkout main
cat > calculator.py <<'PY'
#!/usr/bin/env python3


class Calculator:
    def _validate_number_pair(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Arguments must be numbers")

    def add(self, a, b):
        self._validate_number_pair(a, b)
        return a + b

    def subtract(self, a, b):
        self._validate_number_pair(a, b)
        return a - b


if __name__ == "__main__":
    calc = Calculator()
    print("Calculator Test:")
    print(f"5 + 3 = {calc.add(5, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
PY

chmod +x calculator.py
git add calculator.py
GIT_AUTHOR_DATE="2024-01-10T11:00:00+0000" GIT_COMMITTER_DATE="2024-01-10T11:00:00+0000" git commit -m "Add input validation to calculator"

printf '%s\n' "$(git rev-parse main)" > /workspace/original_main_sha.txt

git checkout feature-advanced-ops
GIT_SEQUENCE_EDITOR=: git rebase -i main || true

test -d .git/rebase-merge
grep -q '^<<<<<<< ' calculator.py
EOF

WORKDIR /workspace
ENV TEST_DIR=/tests
