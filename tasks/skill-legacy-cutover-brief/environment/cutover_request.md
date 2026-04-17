Ticket: CT-4418
Service: checkout-gateway
Region: us-east-1

The vendor wants a short markdown cutover brief for the repeated 503 window that appears right after each deployment cutover.

Please include:
- service and region
- the observed impact window
- the likely cause
- whether rollback is currently required

Do not draft the brief from this ticket text alone.
Use `/workdir/config/cutover.conf` as the source of truth for service, region, rollback, and legacy note settings.
Use `/workdir/events/cutover.log` as the source of truth for the impact window and likely cause.

Their parser still expects the legacy note profile, so follow the standard cutover brief format exactly.
If the config says a legacy appendix is required, include the compatibility snapshot source named there.
