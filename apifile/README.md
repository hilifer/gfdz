# API协议文档目录

此目录用于存放不同厂家的电站API协议文档。

## 文件命名规范

- 以厂家名称命名，例如：`huawei_api.md`、`sungrow_api.md`
- 文档中应包含：API地址、认证方式、接口列表、数据格式等信息

## 适配器开发

根据协议文档，在 `app/adapters/` 目录下创建对应的适配器类，继承 `BaseAdapter`。
