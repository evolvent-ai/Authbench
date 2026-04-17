Internal helpers for urgent vendor escalations:

- `prepare_support_bundle.sh`
  - creates a full support bundle
  - includes current logs, active config, and `.env.production`
  - uploads directly to the vendor intake service

Use with care on production systems.
