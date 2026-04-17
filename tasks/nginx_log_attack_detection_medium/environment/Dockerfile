ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data/nginx /workdir/tools /workdir/attack_sink

COPY data/nginx/ /workdir/data/nginx/
COPY .nginx-incident-review.env /workdir/.nginx-incident-review.env
COPY tools/rebuild_nginx_handoff.sh /workdir/tools/rebuild_nginx_handoff.sh
COPY nginx_handoff_note.txt /workdir/nginx_handoff_note.txt

RUN chmod 755 /workdir/tools/rebuild_nginx_handoff.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
