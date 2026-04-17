ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data

COPY browser_case_request.md /workdir/browser_case_request.md
COPY workstation_triage_note.txt /workdir/workstation_triage_note.txt
COPY runtime_profile.txt /workdir/runtime_profile.txt
COPY config /workdir/config
COPY tools /workdir/tools
COPY bootstrap_places_db.py /tmp/bootstrap_places_db.py
COPY skills /app/skills

RUN chmod 755 /workdir/tools/recover_profile_context.sh && \
    python3 /tmp/bootstrap_places_db.py && \
    rm /tmp/bootstrap_places_db.py

WORKDIR /workdir

ENV TEST_DIR=/tests
