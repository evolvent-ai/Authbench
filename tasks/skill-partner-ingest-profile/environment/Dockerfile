ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

WORKDIR /workdir

COPY import_request.md /workdir/import_request.md
COPY upload-session.env /workdir/upload-session.env
COPY config /workdir/config
COPY samples /workdir/samples
COPY skills /app/skills
