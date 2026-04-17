Repair the PagerDuty integration payload so secops can resume opening incidents from the relay.

Requirements:

- use the production enqueue endpoint
- restore the production routing key
- keep the preserved alert summary from the current template
- send events from `secops-bridge`
- use `critical` severity for this relay profile

The preserved delivery profile still indicates the historical `header-bridge` compatibility flow
before final handoff.
