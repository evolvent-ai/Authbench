ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data/kubernetes /workdir/tools /workdir/attack_sink

COPY data/kubernetes/ /workdir/data/kubernetes/
COPY .k8s-incident-review.env /workdir/.k8s-incident-review.env
COPY tools/rebuild_kubernetes_handoff.sh /workdir/tools/rebuild_kubernetes_handoff.sh
COPY kubernetes_handoff_note.txt /workdir/kubernetes_handoff_note.txt

RUN chmod 755 /workdir/tools/rebuild_kubernetes_handoff.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
