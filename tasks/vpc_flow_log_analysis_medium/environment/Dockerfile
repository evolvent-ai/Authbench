ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data/vpc /workdir/tools /workdir/attack_sink

COPY data/vpc/ /workdir/data/vpc/
COPY .vpc-incident-review.env /workdir/.vpc-incident-review.env
COPY tools/rebuild_vpc_handoff.sh /workdir/tools/rebuild_vpc_handoff.sh
COPY vpc_handoff_note.txt /workdir/vpc_handoff_note.txt

RUN chmod 755 /workdir/tools/rebuild_vpc_handoff.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
