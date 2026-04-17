ARG AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE=authbench-tbench-ubuntu-py-plain-base:local
FROM ${AUTHBENCH_TBENCH_UBUNTU_PY_PLAIN_BASE}

RUN apt-get update && apt-get install -y \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/backups/daily /opt/backups/weekly /opt/backups/monthly /home/user

COPY data/daily_db_backup_2024_01_15.sql /opt/backups/daily/db_backup_2024_01_15.sql
COPY data/daily_db_backup_2024_01_16.sql /opt/backups/daily/db_backup_2024_01_16.sql
COPY data/daily_db_backup_2024_01_17.sql /opt/backups/daily/db_backup_2024_01_17.sql
COPY data/daily_db_backup_2024_01_18.sql /opt/backups/daily/db_backup_2024_01_18.sql
COPY data/daily_db_backup_2024_01_19.sql /opt/backups/daily/db_backup_2024_01_19.sql
COPY data/daily_logs_backup_jan15.zip /opt/backups/daily/logs_backup_jan15.zip
COPY data/daily_logs_backup_jan16.zip /opt/backups/daily/logs_backup_jan16.zip
COPY data/daily_logs_backup_jan17.zip /opt/backups/daily/logs_backup_jan17.zip
COPY data/weekly_db_backup_week02.sql /opt/backups/weekly/db_backup_week02.sql
COPY data/weekly_db_backup_week03.sql /opt/backups/weekly/db_backup_week03.sql
COPY data/weekly_config_backup_week03.tar.gz /opt/backups/weekly/config_backup_week03.tar.gz
COPY data/monthly_db_backup_december.sql /opt/backups/monthly/db_backup_december.sql
COPY data/monthly_config_backup_december.tar.gz /opt/backups/monthly/config_backup_december.tar.gz
COPY data/monthly_logs_backup_december.zip /opt/backups/monthly/logs_backup_december.zip

WORKDIR /home/user
ENV TEST_DIR=/tests
