# gfdz - 光伏电站监控平台

多厂家光伏电站数据统一监控管理平台。

## 功能特性

- **多厂家支持**: 插件式适配器架构，轻松对接不同厂家API（华为、阳光电源、锦浪等）
- **电站管理**: 统一管理多个电站的基本信息、装机容量、联系人等
- **发电监控**: 实时功率、日/月/年发电量、峰值功率、PR值等关键指标
- **告警管理**: 集中展示所有电站告警，支持告警级别分类
- **数据同步**: 定时自动同步 + 手动触发同步
- **可视化仪表盘**: 发电趋势图、状态分布图、关键指标卡片

## 技术栈

- **后端**: Python + FastAPI + SQLAlchemy (异步)
- **数据库**: SQLite (可切换PostgreSQL/MySQL)
- **前端**: Bootstrap 5 + Chart.js + Jinja2模板
- **定时任务**: APScheduler

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py

# 访问 http://localhost:8000
```

## 项目结构

```
gfdz/
├── apifile/                # 厂家API协议文档（下个版本提交）
├── app/
│   ├── adapters/           # 厂家API适配器
│   │   ├── base.py         # 适配器基类
│   │   ├── registry.py     # 适配器注册表
│   │   └── demo_adapter.py # 演示适配器
│   ├── api/                # API路由
│   │   ├── manufacturers.py
│   │   ├── stations.py
│   │   ├── dashboard.py
│   │   └── data_sync.py
│   ├── models/             # 数据库模型
│   ├── schemas/            # 请求/响应Schema
│   ├── services/           # 业务逻辑
│   └── tasks/              # 定时任务
├── templates/              # 前端页面模板
├── static/                 # 静态资源
├── config.py               # 配置
├── run.py                  # 启动入口
└── requirements.txt
```

## 添加新厂家适配器

1. 在 `apifile/` 下放入厂家API协议文档
2. 在 `app/adapters/` 下创建新适配器文件
3. 继承 `BaseAdapter`，用 `@AdapterRegistry.register("厂家编码")` 注册
4. 实现 `authenticate`、`get_station_list`、`get_station_realtime`、`get_station_daily`、`get_station_alarms` 方法
5. 在 `app/main.py` 中 import 新适配器文件
6. 在后台"厂家管理"中添加厂家，编码与注册编码一致
