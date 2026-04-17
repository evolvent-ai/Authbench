FROM ghcr.io/laude-institute/t-bench/ubuntu-24-04:20250624

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3-pip python3-pytest strace && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/sync-service /var/log/sync-service /workdir/tools /tmp

COPY data/sync_service_error.log /var/log/sync-service/sync_service_error.log
COPY data/auth_config.json /opt/sync-service/auth_config.json
COPY sync_service.py /opt/sync-service/sync_service.py
COPY .oauth_sync_review.env /workdir/.oauth_sync_review.env
COPY oauth_ops_note.txt /workdir/oauth_ops_note.txt
COPY tools/rebuild_oauth_diagnosis_bundle.py /workdir/tools/rebuild_oauth_diagnosis_bundle.py

WORKDIR /opt/sync-service

ENV TEST_DIR=/tests
