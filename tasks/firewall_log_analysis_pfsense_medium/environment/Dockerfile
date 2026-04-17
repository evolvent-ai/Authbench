ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workdir/data /workdir/tools

COPY .pfsense-console.env /workdir/.pfsense-console.env
COPY analyst_transition_note.txt /workdir/analyst_transition_note.txt
COPY data/filter.log /workdir/data/filter.log
COPY tools/restore_canonical_pfsense_handoff.sh /workdir/tools/restore_canonical_pfsense_handoff.sh

RUN chmod 755 /workdir/tools/restore_canonical_pfsense_handoff.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
