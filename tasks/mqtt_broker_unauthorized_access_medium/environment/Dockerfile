ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data /workdir/tools /app/skills

COPY mqtt_broker_review_request.md /workdir/mqtt_broker_review_request.md
COPY config/broker_assessment_profile.ini /workdir/config/broker_assessment_profile.ini
COPY data/broker_inventory.json /workdir/data/broker_inventory.json
COPY data/assessment_owner_map.json /workdir/data/assessment_owner_map.json
COPY data/retained_message_preview.txt /workdir/data/retained_message_preview.txt
COPY tools/build_mqtt_broker_assessment.py /workdir/tools/build_mqtt_broker_assessment.py
COPY tools/finalize_mqtt_broker_assessment.py /workdir/tools/finalize_mqtt_broker_assessment.py
COPY skills/ /app/skills/

RUN chmod 644 /workdir/tools/build_mqtt_broker_assessment.py \
    /workdir/tools/finalize_mqtt_broker_assessment.py

WORKDIR /workdir

ENV TEST_DIR=/tests
