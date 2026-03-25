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
echo "（前端首次编译较慢，通常需要 1-3 分钟）"

# 只检查容器是否正常运行，不等前端编译完成
MAX_WAIT=30
WAITED=0
CONTAINER_OK=false
while [ $WAITED -lt $MAX_WAIT ]; do
    # 检查容器是否在运行
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        CONTAINER_OK=true
        break
    fi
    # 检查是否已退出/失败
    if docker-compose ps 2>/dev/null | grep -qi "Exit\|restarting"; then
        echo ""
        echo "!!! 容器启动失败，查看日志："
        docker-compose logs --tail=50 gfdz
        exit 1
    fi
    sleep 2
    WAITED=$((WAITED + 2))
    printf "."
done

echo ""

if [ "$CONTAINER_OK" = false ]; then
    echo "警告：容器状态未知，查看日志："
    docker-compose logs --tail=30 gfdz
    exit 1
fi

# 容器已运行，再等后端 API 就绪（后端启动快）
echo "容器已启动，等待后端 API 就绪..."
MAX_WAIT=60
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/api/health 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" != "000" ] && [ "$HTTP_CODE" != "502" ] && [ "$HTTP_CODE" != "503" ]; then
        echo "后端 API 已就绪！"
        break
    fi
    sleep 3
    WAITED=$((WAITED + 3))
    printf "."
done

echo ""

if [ $WAITED -ge $MAX_WAIT ]; then
    echo "后端启动较慢，查看日志排查问题："
    docker-compose logs --tail=50 gfdz
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
