#!/bin/bash
set -euo pipefail

rm -f /usr/bin/curl
printf 'hosts: files dns\n' > /etc/nsswitch.conf
printf '127.0.0.1 localhost\n' > /etc/hosts
printf 'nameserver 8.8.8.8\n' > /etc/resolv.conf
apt-get update -y
apt-get install -y curl
