FROM python:3.12-slim

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

# 初始化 PostgreSQL
USER postgres
RUN /usr/lib/postgresql/*/bin/initdb -D /var/lib/postgresql/data && \
    echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf && \
    echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf
USER root

# 安装后端 Python 依赖
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装前端 Node 依赖
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# 复制全部源码
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# Nginx 配置
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Supervisor 配置
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 初始化脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
