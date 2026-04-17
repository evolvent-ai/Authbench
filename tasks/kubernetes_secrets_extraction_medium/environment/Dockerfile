ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data /workdir/tools /app/skills

COPY kubernetes_secret_review_request.md /workdir/kubernetes_secret_review_request.md
COPY config/secret_assessment_profile.ini /workdir/config/secret_assessment_profile.ini
COPY data/secret_inventory.json /workdir/data/secret_inventory.json
COPY data/assessment_owner_map.json /workdir/data/assessment_owner_map.json
COPY data/legacy_secret_preview.b64 /workdir/data/legacy_secret_preview.b64
COPY tools/build_kubernetes_secret_assessment.py /workdir/tools/build_kubernetes_secret_assessment.py
COPY tools/finalize_kubernetes_secret_assessment.py /workdir/tools/finalize_kubernetes_secret_assessment.py
COPY skills/ /app/skills/

RUN chmod 644 /workdir/tools/build_kubernetes_secret_assessment.py \
    /workdir/tools/finalize_kubernetes_secret_assessment.py

WORKDIR /workdir

ENV TEST_DIR=/tests
