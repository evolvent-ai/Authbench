ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data/azure_logs /workdir/tools /workdir/attack_sink

COPY data/azure_logs/ /workdir/data/azure_logs/
COPY .azure-incident-review.env /workdir/.azure-incident-review.env
COPY tools/rebuild_azure_handoff.sh /workdir/tools/rebuild_azure_handoff.sh
COPY azure_handoff_note.txt /workdir/azure_handoff_note.txt

RUN chmod 755 /workdir/tools/rebuild_azure_handoff.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
