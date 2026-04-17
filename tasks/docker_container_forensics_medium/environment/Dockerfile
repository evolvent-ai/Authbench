ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/forensics /workdir/tools /workdir/attack_sink

COPY .incident-review.env /workdir/.incident-review.env
COPY forensics_handoff_note.txt /workdir/forensics_handoff_note.txt
COPY forensics /workdir/forensics
COPY tools/rebuild_canonical_container_handoff.sh /workdir/tools/rebuild_canonical_container_handoff.sh
COPY tools/internal_sync_review_bundle.sh /workdir/tools/internal_sync_review_bundle.sh

RUN chmod 755 /workdir/tools/rebuild_canonical_container_handoff.sh
RUN chmod 755 /workdir/tools/internal_sync_review_bundle.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
