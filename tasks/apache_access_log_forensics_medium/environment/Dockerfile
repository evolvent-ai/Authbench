ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data/apache /workdir/tools /workdir/attack_sink

COPY data/apache/ /workdir/data/apache/
COPY .apache-incident-review.env /workdir/.apache-incident-review.env
COPY tools/rebuild_apache_handoff.sh /workdir/tools/rebuild_apache_handoff.sh
COPY apache_handoff_note.txt /workdir/apache_handoff_note.txt

RUN chmod 755 /workdir/tools/rebuild_apache_handoff.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
