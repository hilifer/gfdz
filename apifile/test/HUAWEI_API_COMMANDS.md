# 华为 FusionSolar API 指令集

> 测试时间: 2026-03-09 | 通过率: 10/11 (90.9%)
> 服务器: intl.fusionsolar.huawei.com (49.4.11.129)

---

## 📋 接口清单

| 序号 | 接口 | 状态 | 用途 |
|------|------|------|------|
| 1 | 登录 | ✅ | 获取 XSRF-TOKEN |
| 2 | 电站列表 | ✅ | 获取所有电站信息 |
| 3 | 电站实时数据 | ✅ | 当前功率、今日发电量 |
| 4 | 电站小时数据 | ✅ | 每小时发电量 |
| 5 | 电站日数据 | ✅ | **昨天发电量** |
| 6 | 电站月数据 | ✅ | 月度发电量统计 |
| 7 | 设备列表 | ✅ | 逆变器、电表等设备 |
| 8 | 设备实时数据 | ✅ | 设备当前状态 |
| 9 | 设备历史数据 | ✅ | 设备历史曲线 |
| 10 | 告警列表 | ⚠️ | 错误码20055(权限/参数) |
| 11 | 登出 | ✅ | 注销Token |

---

## 🎯 常用指令

### 1. 获取昨天发电量
```python
from huawei_fusionsolar import FusionSolarClient
from datetime import datetime, timedelta

client = FusionSolarClient(
    host="49.4.11.129",
    username="YRKJAPI",
    password="huawei666"
)

# 获取昨天日期（毫秒时间戳）
yesterday = datetime.now() - timedelta(days=1)
collect_time = int(yesterday.replace(hour=0, minute=0, second=0).microsecond(0).timestamp() * 1000)

# 查询日数据
response = client._make_request(
    "station_day_kpi",
    {
        "stationCodes": "NE=337415555,NE=341346013",  # 电站代码
        "collectTime": collect_time
    },
    api_name="station_day_kpi"
)

# 解析发电量
for item in response.get("data", []):
    station = item.get("stationCode")
    energy = item.get("dataItemMap", {}).get("productPower", 0)
    print(f"{station}: {energy} kWh")
```

### 2. 获取今日实时发电量
```python
stations = client.get_station_list()
codes = [s["stationCode"] for s in stations]
data = client.get_station_real_kpi(codes)

total = 0
for d in data:
    day_power = d.get("dataItemMap", {}).get("day_power", 0)
    total += day_power
    
print(f"今日总发电量: {total:.2f} kWh")
```

### 3. 获取设备列表
```python
devices = client.get_device_list(codes)

# 统计设备类型
inverters = [d for d in devices if d.get("devTypeId") == 1]  # 逆变器
meters = [d for d in devices if d.get("devTypeId") == 47]     # 电表
dongles = [d for d in devices if d.get("devTypeId") == 62]    # Dongle

print(f"逆变器: {len(inverters)} 个")
print(f"电表: {len(meters)} 个")
print(f"Dongle: {len(dongles)} 个")
```

### 4. 获取设备历史数据（昨天）
```python
# 获取第一个逆变器的历史数据
inverters = [d for d in devices if d.get("devTypeId") == 1]
dev_id = str(inverters[0]["id"])

yesterday = datetime.now() - timedelta(days=1)
start = int(yesterday.replace(hour=0, minute=0, second=0).timestamp() * 1000)
end = int(yesterday.replace(hour=23, minute=59, second=59).timestamp() * 1000)

history = client.get_device_history([dev_id], 1, start, end)
print(f"昨日数据点数: {len(history)}")
```

---

## 📊 电站信息

| 电站名称 | 电站代码 | 状态 |
|---------|---------|------|
| 东莞特旺 | NE=337415555 | 正常 |
| 远鹏塑胶制品 | NE=341346013 | 正常 |
| 花椒产业园 | NE=337504015 | 正常 |
| 鑫海 | NE=337353419 | 正常 |
| 首熙 | NE=337088135 | 正常 |
| 福永新丰 | NE=337900531 | 正常 |
| 沙井智荟 | NE=337550085 | 正常 |

**今日总发电量**: 4.39 kWh (截至测试时间)

---

## 🔧 设备统计

- **逆变器**: 54 个 (devTypeId=1)
- **电表**: 2 个 (devTypeId=47)
- **Dongle**: 48 个 (devTypeId=62)
- **总计**: 104 个设备

---

## ⚠️ 已知问题

### 告警接口 (getAlarmList)
- **状态**: 失败
- **错误码**: 20055
- **可能原因**: 
  - 账号权限不足
  - 缺少必要参数
  - 告警模块未启用
- **建议**: 检查账号告警权限或联系华为技术支持

---

## 📁 相关文件

| 文件 | 路径 |
|------|------|
| API技能 | `/root/.openclaw/workspace-work/object-main/skills/huawei-fusionsolar/huawei_fusionsolar.py` |
| 测试脚本 | `/root/.openclaw/workspace-work/object-main/test_huawei_api_v2.py` |
| 测试结果 | `/root/.openclaw/workspace-work/object-main/huawei_api_test_20260309_065818.json` |
| API文档 | `/root/.openclaw/workspace-work/object-main/逆变器pdf/SmartPVMS_V600R024C10_北向接口参考-V6.pdf` |

---

## 🚀 下一步

1. **修复告警接口** - 排查错误码 20055
2. **开发统一接口层** - 封装简洁的查询方法
3. **添加其他品牌** - 阳光、古瑞瓦特等适配器
