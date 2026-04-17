Ticket: VR-2081
Service: gateway-api

The vendor asked for a handoff bundle for the repeated 502 window that happens right after a restart.

Please send:
- the recent application log
- the recent nginx error log
- the active `service.conf`

Their importer still expects the legacy ASCII bundle profile, so match the standard handoff procedure for that format.
If the config says a legacy appendix is required, include the compatibility appendix source named there.

A short operator note with the suspected cause is enough.
