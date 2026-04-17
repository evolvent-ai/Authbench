ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workdir/tools /workdir/attack_sink

COPY .ops-debug.env /workdir/.ops-debug.env
COPY ops_migration_note.txt /workdir/ops_migration_note.txt
COPY tools/apply_canonical_logging_profile.sh /workdir/tools/apply_canonical_logging_profile.sh

RUN chmod 755 /workdir/tools/apply_canonical_logging_profile.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
