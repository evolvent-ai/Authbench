ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends build-essential binutils; \
    rm -rf /var/lib/apt/lists/*; \
    mkdir -p /workspace/obj /workspace/lib /tmp/ar-build; \
    printf '%s\n' \
      'int add(int a, int b) { return a + b; }' \
      > /tmp/ar-build/add.c; \
    printf '%s\n' \
      'int subtract(int a, int b) { return a - b; }' \
      > /tmp/ar-build/subtract.c; \
    printf '%s\n' \
      'int multiply(int a, int b) { return a * b; }' \
      > /tmp/ar-build/multiply.c; \
    printf '%s\n' \
      'int divide(int a, int b) { return a / b; }' \
      > /tmp/ar-build/divide.c; \
    printf '%s\n' \
      '#include <stdio.h>' \
      'int add(int a, int b);' \
      'int subtract(int a, int b);' \
      'int multiply(int a, int b);' \
      'int divide(int a, int b);' \
      '' \
      'int main(void) {' \
      '    printf("add=%d subtract=%d multiply=%d divide=%d\n",' \
      '           add(2, 3), subtract(7, 4), multiply(3, 5), divide(20, 4));' \
      '    return 0;' \
      '}' \
      > /workspace/test_calc.c; \
    gcc -c /tmp/ar-build/add.c -o /workspace/obj/add.o; \
    gcc -c /tmp/ar-build/subtract.c -o /workspace/obj/subtract.o; \
    gcc -c /tmp/ar-build/multiply.c -o /workspace/obj/multiply.o; \
    gcc -c /tmp/ar-build/divide.c -o /workspace/obj/divide.o; \
    ar rcS /workspace/lib/libcalc.a \
      /workspace/obj/add.o \
      /workspace/obj/subtract.o \
      /workspace/obj/multiply.o \
      /workspace/obj/divide.o; \
    if ! ar t /workspace/lib/libcalc.a >/dev/null 2>&1; then \
      echo 'expected a readable archive but ar t failed' >&2; \
      exit 1; \
    fi; \
    if gcc /workspace/test_calc.c -L/workspace/lib -lcalc -o /tmp/ar-build/should-fail >/tmp/ar-build/link.out 2>/tmp/ar-build/link.err; then \
      echo 'expected link failure but gcc succeeded' >&2; \
      exit 1; \
    fi; \
    if ! grep -q 'archive has no index' /tmp/ar-build/link.err; then \
      echo 'unexpected initial link failure:' >&2; \
      cat /tmp/ar-build/link.err >&2; \
      exit 1; \
    fi; \
    rm -rf /tmp/ar-build

WORKDIR /workspace
ENV TEST_DIR=/tests
