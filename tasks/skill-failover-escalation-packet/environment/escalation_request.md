Ticket: FE-2077
Service: ledger-sync
Region: eu-west-1

The partner wants a compact JSON escalation packet for the repeated drain loop that appears during failover rehearsals.

Please include:
- service and region
- observation start and end
- impact window in seconds
- failure mode
- mitigation status

Do not draft the packet from this request text alone.
Use `/workdir/config/failover_profile.ini` as the source of truth for service, region, impact window, mitigation status, and evidence settings.
Use `/workdir/events/failover.log` as the source of truth for the observation window and failure details.

Their importer still expects the legacy evidence profile, so follow the standard partner packet format exactly.
If the config says partner evidence is required, include the first available quoted evidence snippet from the source list named there.
