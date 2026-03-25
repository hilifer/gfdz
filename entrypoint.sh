#!/bin/bash
set -e

PG_BIN=$(ls -d /usr/lib/postgresql/*/bin | head -1)
PG_DATA=/var/lib/postgresql/data

# 如果数据目录为空（volume 新挂载），则初始化
if [ ! -f "$PG_DATA/PG_VERSION" ]; then
    echo "Initializing PostgreSQL data directory..."
    chown postgres:postgres "$PG_DATA"
    chmod 700 "$PG_DATA"
    su - postgres -c "$PG_BIN/initdb -D $PG_DATA"
    echo "host all all 0.0.0.0/0 md5" >> "$PG_DATA/pg_hba.conf"
    echo "listen_addresses='*'" >> "$PG_DATA/postgresql.conf"
fi

# 确保权限正确
chown -R postgres:postgres "$PG_DATA"
chmod 700 "$PG_DATA"

# 启动 PostgreSQL 创建用户和数据库
su - postgres -c "$PG_BIN/pg_ctl start -D $PG_DATA -w -t 30"

su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER:-gfdz}'\" | grep -q 1 || \
    psql -c \"CREATE USER ${POSTGRES_USER:-gfdz} WITH PASSWORD '${POSTGRES_PASSWORD:-gfdz123456}';\""

su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB:-gfdz}'\" | grep -q 1 || \
    psql -c \"CREATE DATABASE ${POSTGRES_DB:-gfdz} OWNER ${POSTGRES_USER:-gfdz};\""

su - postgres -c "$PG_BIN/pg_ctl stop -D $PG_DATA -w"

exec "$@"
