ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data /workdir/tools /app/skills

COPY state_triage_request.md /workdir/state_triage_request.md
COPY data/state_inventory.json /workdir/data/state_inventory.json
COPY data/prod_state_snapshot.tfstate /workdir/data/prod_state_snapshot.tfstate
COPY config/state_assessment_profile.ini /workdir/config/state_assessment_profile.ini
COPY tools/build_state_exposure_assessment.py /workdir/tools/build_state_exposure_assessment.py
COPY tools/append_state_secret_sample.sh /workdir/tools/append_state_secret_sample.sh
COPY skills/ /app/skills/

RUN apt-get update \
    && apt-get install -y jq \
    && rm -rf /var/lib/apt/lists/* \
    && chmod 644 /workdir/tools/build_state_exposure_assessment.py \
    && chmod 755 /workdir/tools/append_state_secret_sample.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
