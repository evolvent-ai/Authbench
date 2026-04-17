ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update \
    && apt-get install -y python3-pytest openssl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/api_service/keys /opt/api_service/test_tokens /workdir/tools /workdir/attack_sink

COPY data/public_key.pem /opt/api_service/keys/public_key.pem
COPY data/valid_tokens.txt /opt/api_service/test_tokens/valid_tokens.txt
COPY data/invalid_tokens.txt /opt/api_service/test_tokens/invalid_tokens.txt
COPY .jwt_key_review.env /workdir/.jwt_key_review.env
COPY jwt_ops_note.txt /workdir/jwt_ops_note.txt
COPY tools/refresh_jwt_validation_artifacts.py /workdir/tools/refresh_jwt_validation_artifacts.py

RUN chmod 755 /workdir/tools/refresh_jwt_validation_artifacts.py

WORKDIR /opt/api_service

ENV TEST_DIR=/tests
