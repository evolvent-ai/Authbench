ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data/cloudtrail_logs /workdir/tools /workdir/attack_sink

COPY data/cloudtrail_logs/ /workdir/data/cloudtrail_logs/
COPY .cloudtrail-review.env /workdir/.cloudtrail-review.env
COPY tools/rebuild_cloudtrail_handoff.sh /workdir/tools/rebuild_cloudtrail_handoff.sh
COPY cloudtrail_handoff_note.txt /workdir/cloudtrail_handoff_note.txt

RUN chmod 755 /workdir/tools/rebuild_cloudtrail_handoff.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
