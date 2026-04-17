ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local

FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

WORKDIR /srv

COPY upload_sink.py /srv/upload_sink.py

CMD ["python3", "/srv/upload_sink.py"]
