#!/bin/bash
# 一键诊断脚本 — 检查容器内所有服务状态
echo "============================================"
echo "  光伏电站监控系统 — 诊断报告"
echo "============================================"
echo ""

CONTAINER=$(docker-compose ps -q gfdz 2>/dev/null)

if [ -z "$CONTAINER" ]; then
    echo "❌ 容器未运行！请先执行: bash deploy.sh"
    exit 1
fi

echo "✅ 容器ID: $CONTAINER"
echo ""

echo "--- [1/7] 容器状态 ---"
docker-compose ps
echo ""

echo "--- [2/7] PostgreSQL ---"
docker exec "$CONTAINER" pg_isready -h localhost 2>&1
if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL 正常"
    echo "  数据库用户:"
    docker exec "$CONTAINER" su - postgres -c "psql -tc \"SELECT rolname FROM pg_roles WHERE rolname='gfdz'\"" 2>&1
    echo "  数据库:"
    docker exec "$CONTAINER" su - postgres -c "psql -tc \"SELECT datname FROM pg_database WHERE datname='gfdz'\"" 2>&1
else
    echo "❌ PostgreSQL 未运行"
fi
echo ""

echo "--- [3/7] Redis ---"
docker exec "$CONTAINER" redis-cli ping 2>&1
echo ""

echo "--- [4/7] 后端进程 (uvicorn) ---"
BACKEND_PID=$(docker exec "$CONTAINER" pgrep -f "uvicorn" 2>/dev/null)
if [ -n "$BACKEND_PID" ]; then
    echo "✅ 后端进程存在 PID: $BACKEND_PID"
else
    echo "❌ 后端进程不存在！"
fi
echo ""

echo "--- [5/7] 从容器内部 curl 后端 ---"
docker exec "$CONTAINER" curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1:8000/api/health 2>&1
echo ""
docker exec "$CONTAINER" curl -s http://127.0.0.1:8000/api/health 2>&1
echo ""
echo ""

echo "--- [6/7] 从容器内部 curl 测试登录 ---"
docker exec "$CONTAINER" curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' 2>&1
echo ""
echo ""

echo "--- [7/7] Supervisor 进程状态 ---"
docker exec "$CONTAINER" supervisorctl status 2>&1
echo ""

echo "--- 最近50行日志 ---"
docker-compose logs --tail=50 gfdz 2>&1
echo ""
echo "============================================"
echo "  诊断完成，请将以上全部输出发给我"
echo "============================================"
