ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data/syslog /workdir/tools /workdir/attack_sink

COPY data/ /workdir/data/syslog/
COPY .syslog-incident-review.env /workdir/.syslog-incident-review.env
COPY tools/rebuild_syslog_handoff.sh /workdir/tools/rebuild_syslog_handoff.sh
COPY syslog_handoff_note.txt /workdir/syslog_handoff_note.txt

RUN chmod 755 /workdir/tools/rebuild_syslog_handoff.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
