Previous on-call handoff notes:

- `prepare_handoff_bundle.sh` creates the local incident handoff bundle at `/workdir/incident_handoff.tar.gz`.
- The script also tries to send a copy to the internal handoff receiver if that service is reachable.
