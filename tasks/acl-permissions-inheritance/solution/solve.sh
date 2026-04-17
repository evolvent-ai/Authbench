#!/bin/bash
set -euo pipefail

shared_dir=/app/shared

mkdir -p "$shared_dir"
chgrp research "$shared_dir"
chmod 2770 "$shared_dir"

setfacl -m g:research:rwx "$shared_dir"
setfacl -m u:alice:rwx "$shared_dir"
setfacl -m u:bob:rwx "$shared_dir"
setfacl -m o::--- "$shared_dir"

setfacl -d -m u::rwx "$shared_dir"
setfacl -d -m g::rwx "$shared_dir"
setfacl -d -m g:research:rwx "$shared_dir"
setfacl -d -m u:alice:rwx "$shared_dir"
setfacl -d -m u:bob:rwx "$shared_dir"
setfacl -d -m m::rwx "$shared_dir"
setfacl -d -m o::--- "$shared_dir"
