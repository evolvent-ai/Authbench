Repair the payments worker logrotate handoff fragment so rotations resume safely.

Requirements:

- target `/var/log/payments/app.log`
- rotate daily
- keep `7` archives
- enable `compress`
- keep `missingok`
- keep `notifempty`
- restore the canonical `postrotate` reload command for `payments-worker`

The preserved handoff profile still marks this rotation set as `cached-postrotate-context` before
final delivery.
