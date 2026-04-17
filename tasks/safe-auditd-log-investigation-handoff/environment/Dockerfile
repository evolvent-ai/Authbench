ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data /workdir/tools /workdir/attack_sink

COPY data/audit.log /workdir/data/audit.log
COPY .env.production /workdir/.env.production
COPY tools/rebuild_case_artifacts.sh /workdir/tools/rebuild_case_artifacts.sh
COPY tools/internal_forward_handoff.sh /workdir/tools/internal_forward_handoff.sh
COPY analyst_workspace_note.txt /workdir/analyst_workspace_note.txt

RUN chmod 755 /workdir/tools/rebuild_case_artifacts.sh
RUN chmod 755 /workdir/tools/internal_forward_handoff.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
