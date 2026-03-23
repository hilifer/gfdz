# 华为逆变器 API 配置

## 服务器信息
- **管理域名**: https://intl.fusionsolar.huawei.com
- **类型**: 华为 FusionSolar 国际站

## 认证信息
- **用户名**: YRKJAPI
- **系统码/密码**: huawei666

## 接口文档参考
- 文档位置: `/root/.openclaw/workspace-work/object-main/逆变器pdf/SmartPVMS_V600R024C10_北向接口参考-V6.pdf`
- 版本: V600R024C10

## 常用接口
1. 登录: `POST /thirdData/login`
2. 电站列表: `POST /thirdData/getStationList`
3. 设备列表: `POST /thirdData/getDevList`
4. 设备实时数据: `POST /thirdData/getDevRealKpi`

## 认证方式
- 先调用登录接口获取 XSRF-TOKEN
- TOKEN 有效期 30 分钟
- 后续请求需在 Header 中携带 XSRF-TOKEN

---
*记录时间: 2026-03-08*
