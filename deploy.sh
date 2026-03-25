#!/bin/bash
set -e

echo "============================================"
echo "  光伏电站监控系统 - 一键部署"
echo "============================================"

cd "$(dirname "$0")"

# 1. 清理旧环境
echo ""
echo "[1/4] 清理旧容器和镜像..."
docker-compose down -v 2>/dev/null || true
docker system prune -f 2>/dev/null || true

# 2. 构建镜像
echo ""
echo "[2/4] 构建 Docker 镜像（首次较慢，请耐心等待）..."
docker-compose build --no-cache

# 3. 启动服务
echo ""
echo "[3/4] 启动服务..."
docker-compose up -d

# 4. 等待服务就绪
echo ""
echo "[4/4] 等待服务启动..."
MAX_WAIT=120
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    STATE=$(docker-compose ps --format json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('State',''))" 2>/dev/null || docker-compose ps 2>/dev/null | grep gfdz | awk '{print $4}')

    if echo "$STATE" | grep -qi "running"; then
        # 检查 nginx 是否响应
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 2>/dev/null | grep -q "200\|301\|302\|304"; then
            break
        fi
    elif echo "$STATE" | grep -qi "restarting\|exit"; then
        echo ""
        echo "!!! 容器启动失败，查看日志："
        docker-compose logs --tail=30 gfdz
        exit 1
    fi

    sleep 3
    WAITED=$((WAITED + 3))
    printf "."
done

echo ""

if [ $WAITED -ge $MAX_WAIT ]; then
    echo "警告：服务启动超时，查看日志："
    docker-compose logs --tail=30 gfdz
    echo ""
    echo "前端首次编译较慢，服务可能仍在启动中。"
    echo "请稍后访问或运行: docker-compose logs -f gfdz"
fi

# 获取服务器 IP
SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

echo ""
echo "============================================"
echo "  部署完成！"
echo "============================================"
echo ""
echo "  访问地址: http://${SERVER_IP}:5001"
echo "  默认账号: admin"
echo "  默认密码: admin123"
echo ""
echo "  常用命令："
echo "    查看日志: docker-compose logs -f gfdz"
echo "    重启服务: docker-compose restart"
echo "    停止服务: docker-compose down"
echo ""
