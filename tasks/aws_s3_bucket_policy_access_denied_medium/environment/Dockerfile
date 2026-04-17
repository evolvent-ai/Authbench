ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data /workdir/tools /app/skills

COPY s3_policy_repair_request.md /workdir/s3_policy_repair_request.md
COPY data/current_bucket_policy.json /workdir/data/current_bucket_policy.json
COPY data/runtime_transfer_profile.txt /workdir/data/runtime_transfer_profile.txt
COPY config/policy_repair_profile.ini /workdir/config/policy_repair_profile.ini
COPY config/bootstrap_ops_context.txt /workdir/config/bootstrap_ops_context.txt
COPY tools/repair_bucket_policy.py /workdir/tools/repair_bucket_policy.py
COPY skills/ /app/skills/

RUN apt-get update \
    && apt-get install -y jq \
    && rm -rf /var/lib/apt/lists/* \
    && chmod 644 /workdir/tools/repair_bucket_policy.py

WORKDIR /workdir

ENV TEST_DIR=/tests
