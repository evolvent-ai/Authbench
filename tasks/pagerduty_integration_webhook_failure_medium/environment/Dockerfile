ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data /workdir/config /workdir/tools /app/skills

COPY pagerduty_webhook_request.md /workdir/pagerduty_webhook_request.md
COPY data/current_webhook_template.json /workdir/data/current_webhook_template.json
COPY data/runtime_pager_profile.txt /workdir/data/runtime_pager_profile.txt
COPY config/pagerduty_delivery_profile.ini /workdir/config/pagerduty_delivery_profile.ini
COPY config/legacy_delivery_context.txt /workdir/config/legacy_delivery_context.txt
COPY tools/repair_pagerduty_webhook.py /workdir/tools/repair_pagerduty_webhook.py
COPY tools/reconcile_legacy_delivery_context.py /workdir/tools/reconcile_legacy_delivery_context.py
COPY skills/ /app/skills/

RUN chmod 755 /workdir/tools/reconcile_legacy_delivery_context.py \
    && chmod 644 /workdir/tools/repair_pagerduty_webhook.py

WORKDIR /workdir

ENV TEST_DIR=/tests
