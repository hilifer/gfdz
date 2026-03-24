#!/bin/bash
set -e

PG_BIN=$(ls -d /usr/lib/postgresql/*/bin | head -1)

# 启动 PostgreSQL 创建用户和数据库
su - postgres -c "$PG_BIN/pg_ctl start -D /var/lib/postgresql/data -w -t 30"

su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER:-gfdz}'\" | grep -q 1 || \
    psql -c \"CREATE USER ${POSTGRES_USER:-gfdz} WITH PASSWORD '${POSTGRES_PASSWORD:-gfdz123456}';\""

su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB:-gfdz}'\" | grep -q 1 || \
    psql -c \"CREATE DATABASE ${POSTGRES_DB:-gfdz} OWNER ${POSTGRES_USER:-gfdz};\""

su - postgres -c "$PG_BIN/pg_ctl stop -D /var/lib/postgresql/data -w"

exec "$@"
