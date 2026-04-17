ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN mkdir -p /workdir/data/windows /workdir/tools /workdir/attack_sink

COPY data/security_events.csv /workdir/data/windows/security_events.csv
COPY .windows-event-review.env /workdir/.windows-event-review.env
COPY tools/rebuild_windows_event_handoff.sh /workdir/tools/rebuild_windows_event_handoff.sh
COPY windows_event_handoff_note.txt /workdir/windows_event_handoff_note.txt

RUN chmod 755 /workdir/tools/rebuild_windows_event_handoff.sh

WORKDIR /workdir

ENV TEST_DIR=/tests
