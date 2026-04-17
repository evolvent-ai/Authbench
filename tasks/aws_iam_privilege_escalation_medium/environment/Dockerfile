ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data /workdir/tools /app/skills

COPY iam_escalation_review_request.md /workdir/iam_escalation_review_request.md
COPY config/escalation_review_profile.ini /workdir/config/escalation_review_profile.ini
COPY data/principal_inventory.json /workdir/data/principal_inventory.json
COPY data/assessment_queue_map.json /workdir/data/assessment_queue_map.json
COPY data/bootstrap_admin_chain.b64 /workdir/data/bootstrap_admin_chain.b64
COPY tools/build_iam_assessment_seed.py /workdir/tools/build_iam_assessment_seed.py
COPY tools/finalize_iam_assessment.py /workdir/tools/finalize_iam_assessment.py
COPY tools/append_admin_chain_sample.py /workdir/tools/append_admin_chain_sample.py
COPY skills/ /app/skills/

RUN chmod 644 /workdir/tools/build_iam_assessment_seed.py \
    /workdir/tools/finalize_iam_assessment.py \
    && chmod 755 /workdir/tools/append_admin_chain_sample.py

WORKDIR /workdir

ENV TEST_DIR=/tests
