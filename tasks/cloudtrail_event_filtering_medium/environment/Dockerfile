ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data/cloudtrail_logs /workdir/tools /workdir/config /app/skills

COPY data/cloudtrail_logs/ /workdir/data/cloudtrail_logs/
COPY .cloudtrail-review.env /workdir/.cloudtrail-review.env
COPY filter_case_request.md /workdir/filter_case_request.md
COPY runtime_filter_profile.txt /workdir/runtime_filter_profile.txt
COPY config/filter_profile.ini /workdir/config/filter_profile.ini
COPY config/review_bridge_sources.txt /workdir/config/review_bridge_sources.txt
COPY tools/build_cloudtrail_filter_report.py /workdir/tools/build_cloudtrail_filter_report.py
COPY tools/apply_legacy_filter_context.sh /workdir/tools/apply_legacy_filter_context.sh
COPY skills/ /app/skills/

RUN chmod 755 /workdir/tools/apply_legacy_filter_context.sh \
    && chmod 644 /workdir/tools/build_cloudtrail_filter_report.py

WORKDIR /workdir

ENV TEST_DIR=/tests
