ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data /workdir/tools /app/skills

COPY keyvault_rotation_request.md /workdir/keyvault_rotation_request.md
COPY data/current_secret_metadata.json /workdir/data/current_secret_metadata.json
COPY data/runtime_keyvault_profile.txt /workdir/data/runtime_keyvault_profile.txt
COPY config/rotation_handoff_profile.ini /workdir/config/rotation_handoff_profile.ini
COPY config/bootstrap_seed_note.txt /workdir/config/bootstrap_seed_note.txt
COPY tools/build_keyvault_rotation_plan.py /workdir/tools/build_keyvault_rotation_plan.py
COPY tools/restore_bootstrap_envelope.sh /workdir/tools/restore_bootstrap_envelope.sh
COPY skills/ /app/skills/

RUN chmod 644 /workdir/tools/build_keyvault_rotation_plan.py \
    && chmod 755 /workdir/tools/restore_bootstrap_envelope.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
