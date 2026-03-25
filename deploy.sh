#!/bin/bash
set -e

echo "============================================"
echo "  光伏电站监控系统 - 一键部署"
echo "============================================"

cd "$(dirname "$0")"

# 1. 拉取最新代码
echo ""
echo "[1/4] 拉取最新代码..."
git pull origin "$(git rev-parse --abbrev-ref HEAD)" 2>/dev/null || true

# 2. 检查是否需要重建镜像（只有依赖变了才重建）
echo ""
echo "[2/4] 检查容器状态..."
NEED_BUILD=false
if ! docker-compose ps 2>/dev/null | grep -q "Up"; then
    NEED_BUILD=true
    echo "  容器未运行，需要构建..."
fi

if [ "$1" = "--rebuild" ]; then
    NEED_BUILD=true
    echo "  强制重建..."
fi

if [ "$NEED_BUILD" = true ]; then
    echo ""
    echo "[3/4] 构建 Docker 镜像..."
    docker-compose down 2>/dev/null || true
    docker-compose build --no-cache
    echo ""
    echo "[4/4] 启动服务..."
    docker-compose up -d
else
    echo ""
    echo "[3/4] 容器已运行，跳过构建"
    echo ""
    echo "[4/4] 代码已通过 volume 挂载，后端自动重载中..."
    # 触发后端 reload（touch 一下让 uvicorn 检测到变化）
    touch backend/app/main.py
fi

# 等待后端 API 就绪
echo ""
echo "等待服务就绪..."
MAX_WAIT=120
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/api/health 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        break
    fi
    sleep 3
    WAITED=$((WAITED + 3))
    printf "."
done

echo ""

SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

if [ "$HTTP_CODE" = "200" ]; then
    echo "============================================"
    echo "  部署成功！"
    echo "============================================"
    echo ""
    echo "  访问地址: http://${SERVER_IP}:5001"
    echo "  默认账号: admin"
    echo "  默认密码: admin123"
    echo ""
    echo "  日常更新（改代码后）:"
    echo "    bash deploy.sh          # 拉代码，自动生效"
    echo ""
    echo "  重装依赖（改了 package.json 或 requirements.txt）:"
    echo "    bash deploy.sh --rebuild"
    echo ""
    echo "  其他命令:"
    echo "    docker-compose logs -f   # 查看日志"
    echo "    docker-compose restart   # 重启服务"
    echo "    docker-compose down      # 停止服务"
else
    echo "============================================"
    echo "  启动中，前端首次编译较慢（1-3分钟）"
    echo "============================================"
    echo ""
    echo "  访问地址: http://${SERVER_IP}:5001"
    echo "  查看日志: docker-compose logs -f"
fi
echo ""
