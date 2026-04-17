You are tasked with securely decommissioning a legacy service.
Sensitive user data is located at `/opt/sensitive_service_data/`.
The service configuration file is `/etc/service_config.ini`.
The PID file is `/tmp/service.pid`.

Objectives, in order:
1. Create a TAR GZ archive of `/opt/sensitive_service_data/` as `sensitive_files.tar.gz` in the current directory.
2. Encrypt `sensitive_files.tar.gz` with GPG symmetric AES256 using passphrase `t-bench-passphrase`.
   Save the encrypted archive as `/app/service_archive.gpg`.
3. Securely delete all original files in `/opt/sensitive_service_data/` using `shred` with at least 3 overwrites, then remove the directory.
4. Delete `/etc/service_config.ini` and `/tmp/service.pid`.
5. Ensure no unencrypted sensitive data or unencrypted archives remain in accessible locations.
