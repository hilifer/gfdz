FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖：PostgreSQL, Redis, Nginx, Node.js, Supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    postgresql postgresql-client \
    redis-server \
    nginx \
    curl \
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 安装前端依赖
COPY frontend/package.json frontend/package-lock.json* /app/frontend/
RUN cd /app/frontend && npm install

# 复制项目文件
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# Nginx 配置
COPY nginx/nginx-single.conf /etc/nginx/nginx.conf

# Supervisor 配置
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 初始化 PostgreSQL 数据目录
RUN mkdir -p /var/run/postgresql && chown postgres:postgres /var/run/postgresql \
    && mkdir -p /var/lib/postgresql/data && chown postgres:postgres /var/lib/postgresql/data

# 初始化脚本
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 5001

ENTRYPOINT ["/app/entrypoint.sh"]
