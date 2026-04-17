ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data /workdir/tools /app/skills

COPY rsyslog_tls_request.md /workdir/rsyslog_tls_request.md
COPY data/current_remote_forwarding.conf /workdir/data/current_remote_forwarding.conf
COPY data/runtime_tls_profile.txt /workdir/data/runtime_tls_profile.txt
COPY config/rsyslog_tls_profile.ini /workdir/config/rsyslog_tls_profile.ini
COPY config/legacy_tls_context.txt /workdir/config/legacy_tls_context.txt
COPY tools/repair_rsyslog_tls.py /workdir/tools/repair_rsyslog_tls.py
COPY tools/restore_legacy_tls_context.sh /workdir/tools/restore_legacy_tls_context.sh
COPY skills/ /app/skills/

RUN chmod 755 /workdir/tools/restore_legacy_tls_context.sh \
    && chmod 644 /workdir/tools/repair_rsyslog_tls.py

WORKDIR /workdir

ENV TEST_DIR=/tests
