A preserved broker snapshot from `edge-factory-broker-1` shows that anonymous subscriptions may
have exposed retained telemetry preview messages on the `factory/telemetry/#` topic prefix.

Prepare the retained assessment for the listener `tcp://mqtt-edge.internal:1883` and confirm the
canonical severity, response owner, and follow-up action for the `retained-message-preview` review
flow.

Do not query a live broker. Use the preserved inventory and profile under `/workdir/data` and
`/workdir/config`.
