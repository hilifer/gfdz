#!/bin/bash
set -e

# 初始化 PostgreSQL（如果数据目录为空）
if [ ! -f /var/lib/postgresql/data/PG_VERSION ]; then
    su postgres -c "initdb -D /var/lib/postgresql/data"
    # 配置 PostgreSQL 允许本地连接
    echo "host all all 127.0.0.1/32 md5" >> /var/lib/postgresql/data/pg_hba.conf
    echo "local all all trust" >> /var/lib/postgresql/data/pg_hba.conf

    # 启动临时 PostgreSQL 创建数据库和用户
    su postgres -c "pg_ctl -D /var/lib/postgresql/data start -w"
    su postgres -c "psql -c \"CREATE USER gfdz WITH PASSWORD 'gfdz123456';\""
    su postgres -c "psql -c \"CREATE DATABASE gfdz OWNER gfdz;\""
    su postgres -c "pg_ctl -D /var/lib/postgresql/data stop -w"
fi

# 启动所有服务
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
