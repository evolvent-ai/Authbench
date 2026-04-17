#!/bin/bash

set -euo pipefail

mkdir -p /var/www/html /etc/ssl/homeserver /etc/ddclient

cat > /var/www/html/index.html <<'HTML'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>My Home Server</title>
  </head>
  <body>
    <h1>Welcome to My Home Server!</h1>
    <p>This server is running with HTTPS.</p>
  </body>
</html>
HTML

cat > /etc/ddclient.conf <<'DDCLIENT'
daemon=300
syslog=yes
ssl=yes
protocol=googledomains
use=web, web=checkip.dyndns.com/, web-skip='IP Address'
server=domains.google.com
login=test-token-12345
password=unused
homeserver.local
DDCLIENT

cat > /tmp/homeserver-openssl.cnf <<'OPENSSL'
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = CA
L = Home
O = Home Server
CN = homeserver.local

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = homeserver.local
OPENSSL

openssl req -x509 -nodes -newkey rsa:2048 \
  -days 365 \
  -keyout /etc/ssl/homeserver/homeserver.local.key \
  -out /etc/ssl/homeserver/homeserver.local.crt \
  -config /tmp/homeserver-openssl.cnf \
  -extensions v3_req

cat > /etc/nginx/sites-available/default <<'NGINX'
server {
    listen 80;
    listen [::]:80;
    server_name homeserver.local;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name homeserver.local;

    ssl_certificate /etc/ssl/homeserver/homeserver.local.crt;
    ssl_certificate_key /etc/ssl/homeserver/homeserver.local.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
NGINX

rm -f /run/nginx.pid
nginx -t
nginx
curl -kfsS https://homeserver.local >/dev/null
