ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/config /workdir/data /workdir/tools /app/skills

COPY blob_review_request.md /workdir/blob_review_request.md
COPY config/blob_review_profile.ini /workdir/config/blob_review_profile.ini
COPY config/legacy_sas_snapshot.env /workdir/config/legacy_sas_snapshot.env
COPY data/blob_inventory.json /workdir/data/blob_inventory.json
COPY data/assessment_queue_map.json /workdir/data/assessment_queue_map.json
COPY data/runtime_blob_profile.txt /workdir/data/runtime_blob_profile.txt
COPY tools/build_blob_sas_review.py /workdir/tools/build_blob_sas_review.py
COPY tools/finalize_blob_sas_review.py /workdir/tools/finalize_blob_sas_review.py
COPY tools/merge_legacy_sas_snapshot.awk /workdir/tools/merge_legacy_sas_snapshot.awk
COPY skills/ /app/skills/

RUN chmod 644 /workdir/tools/build_blob_sas_review.py \
    /workdir/tools/finalize_blob_sas_review.py \
    /workdir/tools/merge_legacy_sas_snapshot.awk

WORKDIR /workdir

ENV TEST_DIR=/tests
