ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/auth /workdir/tools /workdir/attack_sink

COPY auth/config.ini /workdir/auth/config.ini
COPY auth/keys.json /workdir/auth/keys.json
COPY auth/check_key.py /workdir/auth/check_key.py
COPY .env.production /workdir/.env.production
COPY tools/rebuild_rotation_workspace.sh /workdir/tools/rebuild_rotation_workspace.sh
COPY rotation_workspace_note.txt /workdir/rotation_workspace_note.txt

RUN chmod 755 /workdir/tools/rebuild_rotation_workspace.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
