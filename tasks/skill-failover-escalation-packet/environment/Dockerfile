ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

WORKDIR /workdir

COPY escalation_request.md /workdir/escalation_request.md
COPY dr-rehearsal-note.txt /workdir/dr-rehearsal-note.txt
COPY runtime-profile.txt /workdir/runtime-profile.txt
COPY config /workdir/config
COPY events /workdir/events
COPY skills /app/skills
