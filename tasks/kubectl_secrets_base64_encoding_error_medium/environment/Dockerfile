ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data /workdir/tools /app/skills

COPY secret_repair_request.md /workdir/secret_repair_request.md
COPY data/payment-gateway-secret.yaml /workdir/data/payment-gateway-secret.yaml
COPY data/runtime_kubectl_profile.txt /workdir/data/runtime_kubectl_profile.txt
COPY config/secret_repair_profile.ini /workdir/config/secret_repair_profile.ini
COPY config/legacy_apply_context.conf /workdir/config/legacy_apply_context.conf
COPY tools/repair_secret_manifest.py /workdir/tools/repair_secret_manifest.py
COPY tools/append_last_applied_context.sh /workdir/tools/append_last_applied_context.sh
COPY skills/ /app/skills/

RUN chmod 755 /workdir/tools/append_last_applied_context.sh \
    && chmod 644 /workdir/tools/repair_secret_manifest.py

WORKDIR /workdir

ENV TEST_DIR=/tests
