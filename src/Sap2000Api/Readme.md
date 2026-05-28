# SAP2000 API

## 文件组成

```
LIB/
├── protocols.py       # 定义接口协议（解决循环导入）
├── base.py            # 子模块基类
├── material.py        # 材质管理
├── section.py         # 截面管理
├── point.py           # 节点/点对象管理
├── frame.py           # 框架/线对象管理
├── load.py            # 荷载管理
├── group.py           # 组管理
└── Sap2000Api.py      # 主入口文件（聚合所有功能）
```