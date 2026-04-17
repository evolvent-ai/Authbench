ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update -y \
    && apt-get install -y \
    autoconf \
    automake \
    build-essential \
    libtool \
    && rm -rf /var/lib/apt/lists/*

COPY opt /opt

# The source task's checked-in configure script is truncated.
# Regenerate it here so the user-facing task is still about fixing execute bits.
RUN cd /opt/legacy-calculator && autoconf

# Preserve the original task's blocking condition from source control mode bits.
RUN chmod 0644 /opt/legacy-calculator/configure

WORKDIR /app
ENV TEST_DIR=/tests
