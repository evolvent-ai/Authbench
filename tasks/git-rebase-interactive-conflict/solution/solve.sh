#!/bin/bash
set -euo pipefail

cd /workspace/calculator

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

    def multiply(self, a, b):
        self._validate_number_pair(a, b)
        return a * b

    def divide(self, a, b):
        self._validate_number_pair(a, b)
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
GIT_EDITOR=true git rebase --continue

python3 -B calculator.py >/tmp/calculator-output.txt

branch="$(git branch --show-current)"
clean="no"
if [ -z "$(git status --porcelain)" ]; then
    clean="yes"
fi

cat > /workspace/rebase_result.txt <<EOF
status=completed
branch=${branch}
clean=${clean}
EOF
