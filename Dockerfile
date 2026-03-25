FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖：PostgreSQL, Redis, Nginx, Node.js, Supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    postgresql postgresql-client \
    redis-server \
    nginx \
    curl \
    supervisor \
    locales \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# 安装后端 Python 依赖
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装前端 Node 依赖到独立目录（不会被 volume 覆盖）
WORKDIR /deps/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN node -v && npm -v && npm install && ls -la node_modules/.bin/nuxt

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
