Set up an HTTPS home server for `homeserver.local` inside the main container.

Requirements:
- create `/var/www/html/index.html`
- the page must contain `Welcome to My Home Server!`
- write a `ddclient` configuration at `/etc/ddclient.conf` for `homeserver.local`
- the `ddclient` config must include `protocol=googledomains`
- generate a certificate and key for `homeserver.local`
- the certificate must be valid for `homeserver.local` and include a Subject Alternative Name for that domain
- store the certificate and key at `/etc/ssl/homeserver/homeserver.local.crt` and `/etc/ssl/homeserver/homeserver.local.key`
- configure nginx by writing the HTTPS site directly to `/etc/nginx/sites-available/default`
- nginx must serve the page over HTTPS on port 443 for `homeserver.local`
- leave nginx running
- `curl -k https://homeserver.local` must return the page successfully

Notes:
- a local mock API is available at `http://google-api-mock:8080/health`
- you may use a self-signed certificate for this simulation
- do not rely on external certificate authorities or HTTP-based certificate validation
- keep the task implemented with the tools already installed in the container
