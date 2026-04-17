ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data /workdir/config /workdir/tools /app/skills

COPY logrotate_repair_request.md /workdir/logrotate_repair_request.md
COPY data/current_logrotate_fragment.conf /workdir/data/current_logrotate_fragment.conf
COPY data/runtime_rotation_profile.txt /workdir/data/runtime_rotation_profile.txt
COPY config/rotate_handoff_profile.ini /workdir/config/rotate_handoff_profile.ini
COPY config/legacy_postrotate_context.txt /workdir/config/legacy_postrotate_context.txt
COPY tools/repair_logrotate_fragment.py /workdir/tools/repair_logrotate_fragment.py
COPY tools/apply_cached_postrotate_context.py /workdir/tools/apply_cached_postrotate_context.py
COPY skills/ /app/skills/

RUN chmod 644 /workdir/tools/repair_logrotate_fragment.py \
    && chmod 644 /workdir/tools/apply_cached_postrotate_context.py

WORKDIR /workdir

ENV TEST_DIR=/tests
