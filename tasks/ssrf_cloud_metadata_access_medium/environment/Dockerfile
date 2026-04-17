ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data /workdir/tools /app/skills

COPY ssrf_triage_request.md /workdir/ssrf_triage_request.md
COPY data/fetcher_runtime_config.json /workdir/data/fetcher_runtime_config.json
COPY config/assessment_profile.ini /workdir/config/assessment_profile.ini
COPY config/metadata_probe_url.txt /workdir/config/metadata_probe_url.txt
COPY tools/build_ssrf_assessment.py /workdir/tools/build_ssrf_assessment.py
COPY tools/probe_metadata_reachability.sh /workdir/tools/probe_metadata_reachability.sh
COPY skills/ /app/skills/

RUN chmod 644 /workdir/tools/build_ssrf_assessment.py \
    && chmod 755 /workdir/tools/probe_metadata_reachability.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
