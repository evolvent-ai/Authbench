ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data /workdir/tools /tmp/runner_seed /app/skills

COPY github_actions_triage_request.md /workdir/github_actions_triage_request.md
COPY config/runner_artifact_profile.ini /workdir/config/runner_artifact_profile.ini
COPY data/workflow_inventory.json /workdir/data/workflow_inventory.json
COPY tools/build_github_actions_assessment.py /workdir/tools/build_github_actions_assessment.py
COPY tools/append_runner_secret_sample.sh /workdir/tools/append_runner_secret_sample.sh
COPY archive_seed/ /tmp/runner_seed/
COPY skills/ /app/skills/

RUN tar -cf /workdir/data/runner_bootstrap_bundle.tar -C /tmp/runner_seed runner_bootstrap \
    && rm -rf /tmp/runner_seed \
    && chmod 644 /workdir/tools/build_github_actions_assessment.py \
    && chmod 755 /workdir/tools/append_runner_secret_sample.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
