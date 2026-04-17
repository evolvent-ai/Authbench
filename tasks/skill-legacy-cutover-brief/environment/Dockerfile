ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

WORKDIR /workdir

COPY cutover_request.md /workdir/cutover_request.md
COPY runtime-profile.txt /workdir/runtime-profile.txt
COPY config /workdir/config
COPY events /workdir/events
COPY skills /app/skills
