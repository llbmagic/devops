# CMDB 模块设计方案

## 1. 概述

CMDB（配置管理数据库）模块对企业 IT 资产进行全生命周期管理，提供统一的资产配置、状态、关联关系视图，支持基于位置、业务、标签的关系建模和服务树构建。通过 API 与 Agent 协同的自动发现机制，实现对包括多云环境在内的 IT 资产自动纳管。

### 1.1 解决的核心问题
- **资产信息分散、数据孤立**：告别 Excel、多系统碎片化记录，构建统一的配置管理中心。
- **难以统一管理**：整合传统数据中心、私有云、公有云等多类型资产，提供标准化管理入口。
- **资产变更难以跟踪**：无感知变更导致配置漂移和故障排查困难，需实现变更记录与审计。
- **多云资产管理复杂**：不同云厂商模型差异大，难以统一查看和操作，需通过模型映射消除异构。

### 1.2 术语定义
- **CI（配置项）**：IT 环境中需要管理的任何组件，如服务器、数据库、云实例、应用服务等。
- **资产全生命周期**：从资产发现/录入、上线、变更、维保、下线到归档的全过程状态管理。
- **服务树**：以业务为中心的层级拓扑，描述业务系统、应用服务、运行实例之间的层次关系。
- **位置树**：按物理或逻辑区域组织的层级关系，如园区-机房-机柜，或云环境 Region-Zone。
- **标签**：附加于资产的键值对，用于灵活分组、分类及策略驱动。

---

## 2. 总体设计目标
- **统一模型**：建立可扩展的资产元模型，融合物理机、虚拟机、云资源、网络设备、存储设备等。
- **全生命周期**：从发现或录入到退役，覆盖资产的待审核、在线、离线、维护中、下线、归档等状态。
- **多维关联**：支持基于位置、业务、标签自动或手动构建资产关联，形成拓扑和服务树。
- **自动纳管**：通过 Agent 上报和云 API 调用实现资产自动发现、属性同步和变更感知。
- **多云透明**：用户可在单一界面查看 AWS、阿里云等多云账号下的资产，屏蔽底层差异。
- **变更追溯**：记录每次属性变更、关系变更，提供差异对比和审计日志。

---

## 3. 数据模型设计

### 3.1 核心实体

#### Asset（统一资产表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| name | CharField(200) | 资产名称 |
| asset_type | CharField(20) | 资产类型 |
| unique_id | CharField(200) | 唯一标识（序列号/InstanceId） |
| status | CharField(20) | 生命周期状态 |
| location | ForeignKey | 所属位置节点 |
| business_node | ForeignKey | 所属服务树节点 |
| properties | JSONField | 类型特有属性 |
| cloud_info | JSONField | 云厂商原始信息 |
| owner | CharField(100) | 负责人 |
| maintenance_expire | DateField | 维保过期日期（可选） |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |
| discovered_at | DateTimeField | 发现时间 |
| is_deleted | BooleanField | 软删除标记 |

**资产类型（asset_type）：**
- `server` - 物理服务器
- `vm` - 虚拟机
- `cloud_vm` - 云主机
- `network_device` - 网络设备
- `storage` - 存储设备

**状态（status）：**
- `pending` - 待审核
- `online` - 在线
- `offline` - 离线
- `maintenance` - 维护中
- `decommissioned` - 已下线
- `archived` - 已归档

#### AssetTypeDefinition（资产类型定义）

| 字段 | 类型 | 说明 |
|------|------|------|
| asset_type | CharField(20) | 资产类型代码 |
| name | CharField(100) | 类型名称 |
| property_schema | JSONField | 属性schema定义 |
| icon | CharField(50) | 前端图标 |

#### Relationship（关系表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| source | ForeignKey | 源资产 |
| target | ForeignKey | 目标资产 |
| type | CharField(20) | 关系类型 |
| description | TextField | 关系描述 |
| created_at | DateTimeField | 创建时间 |

**关系类型（type）：**
- `runs_on` - 运行于（vm runs_on server）
- `depends_on` - 依赖（app depends_on database）
- `connects_to` - 连接（server connects_to switch）

#### LocationNode（位置树节点）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| parent | ForeignKey | 父节点（可为空） |
| name | CharField(100) | 节点名称 |
| type | CharField(20) | 节点类型 |
| code | CharField(50) | 编码（唯一） |
| description | TextField | 描述 |
| created_at | DateTimeField | 创建时间 |

**位置类型（type）：**
- `region` - 区域（如华北、华南）
- `zone` - 可用区
- `datacenter` - 机房
- `rack` - 机柜
- `device` - 设备位

#### BusinessServiceNode（服务树节点）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| parent | ForeignKey | 父节点（可为空） |
| name | CharField(100) | 节点名称 |
| type | CharField(20) | 节点类型 |
| code | CharField(50) | 编码（唯一） |
| description | TextField | 描述 |
| created_at | DateTimeField | 创建时间 |

**服务树节点类型（type）：**
- `business` - 业务线
- `service` - 服务
- `module` - 模块
- `instance` - 实例

#### Tag / AssetTag（标签管理）

Tag 定义：
| 字段 | 类型 | 说明 |
|------|------|------|
| key | CharField(50) | 标签键 |
| value | CharField(100) | 标签值 |

AssetTag 关联表：
| 字段 | 类型 | 说明 |
|------|------|------|
| asset | ForeignKey | 资产 |
| tag | ForeignKey | 标签 |
| created_at | DateTimeField | 创建时间 |

#### CloudAccount（云账号配置）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| provider | CharField(20) | 云厂商（aws/aliyun/tencent） |
| name | CharField(100) | 账号名称 |
| credentials | JSONField | 加密存储的密钥 |
| regions | JSONField | 关联区域列表 |
| is_active | BooleanField | 是否启用 |
| last_sync_at | DateTimeField | 最后同步时间 |
| created_at | DateTimeField | 创建时间 |

#### CloudResourceMapping（多云映射规则）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| cloud_account | ForeignKey | 云账号 |
| source_type | CharField(100) | 原始资源类型（如 AWS::EC2::Instance） |
| target_asset_type | CharField(20) | 目标资产类型 |
| field_mappings | JSONField | 属性映射规则 |
| is_active | BooleanField | 是否启用 |

#### AssetChangeLog（变更审计日志）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| asset | ForeignKey | 资产 |
| field | CharField(100) | 变更字段 |
| old_value | TextField | 旧值 |
| new_value | TextField | 新值 |
| operator | CharField(100) | 操作人 |
| source | CharField(20) | 操作来源（manual/api/agent） |
| created_at | DateTimeField | 操作时间 |

### 3.2 状态流转

```
pending → online → maintenance → decommissioned → archived
    ↓         ↓          ↓
  rejected   offline    offline
```

**状态变更操作：**
- `approve` - 审核通过（pending → online）
- `reject` - 审核拒绝（pending → archived）
- `online` - 上线
- `offline` - 下线
- `maintenance` - 进入维护
- `decommission` - 退役
- `archive` - 归档

---

## 4. API 设计

统一前缀 `/api/cmdb/v1`

### 4.1 资产管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/assets/` | 资产列表（支持分页、筛选） |
| POST | `/assets/` | 创建资产 |
| GET | `/assets/{id}/` | 资产详情 |
| PUT | `/assets/{id}/` | 更新资产 |
| DELETE | `/assets/{id}/` | 软删除资产 |
| POST | `/assets/{id}/lifecycle/` | 生命周期操作 |
| GET | `/assets/{id}/relationships/` | 资产关联关系 |
| GET | `/assets/{id}/history/` | 变更历史 |
| POST | `/assets/auto-discover/` | Agent 批量上报 |

### 4.2 关系管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/relationships/` | 关系列表 |
| POST | `/relationships/` | 创建关系 |
| DELETE | `/relationships/{id}/` | 删除关系 |

### 4.3 位置树

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/locations/` | 位置树列表（树形结构） |
| POST | `/locations/` | 创建位置节点 |
| GET | `/locations/{id}/` | 位置节点详情 |
| PUT | `/locations/{id}/` | 更新位置节点 |
| DELETE | `/locations/{id}/` | 删除位置节点 |

### 4.4 服务树

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/business-tree/` | 服务树列表（树形结构） |
| POST | `/business-tree/` | 创建服务节点 |
| GET | `/business-tree/{id}/` | 服务节点详情 |
| PUT | `/business-tree/{id}/` | 更新服务节点 |
| DELETE | `/business-tree/{id}/` | 删除服务节点 |
| POST | `/business-tree/{id}/attach/` | 挂载资产 |

### 4.5 标签管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tags/` | 标签列表 |
| POST | `/tags/` | 创建标签 |
| DELETE | `/tags/{id}/` | 删除标签 |

### 4.6 云账号管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/cloud-accounts/` | 云账号列表 |
| POST | `/cloud-accounts/` | 创建云账号 |
| GET | `/cloud-accounts/{id}/` | 云账号详情 |
| PUT | `/cloud-accounts/{id}/` | 更新云账号 |
| DELETE | `/cloud-accounts/{id}/` | 删除云账号 |
| POST | `/cloud-accounts/{id}/sync/` | 触发同步 |
| GET | `/cloud-accounts/{id}/mappings/` | 映射规则列表 |

### 4.7 变更历史

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/change-logs/` | 变更日志列表 |
| GET | `/change-logs/{id}/` | 变更详情 |

---

## 5. 自动纳管设计

### 5.1 Agent 模式

Agent 批量上报接口 `/assets/auto-discover/`

请求格式：
```json
{
  "agent_id": "agent-001",
  "discoveries": [
    {
      "unique_id": "SN-12345",
      "name": "web-server-01",
      "asset_type": "server",
      "properties": {
        "cpu": "8核",
        "memory": "32GB",
        "disk": "500GB SSD",
        "os": "CentOS 7.9",
        "serial_number": "SN-12345"
      },
      "location_code": "SZ-DC01-RACK-A12",
      "tags": ["env:prod", "team:sre"]
    }
  ]
}
```

### 5.2 云厂商 API 模式

支持 AWS 示例适配器：

1. 用户在 CloudAccount 中配置 AWS 账号和凭证
2. 系统调用 AWS API（describeInstances）获取资源列表
3. 根据 CloudResourceMapping 规则转换为标准 Asset
4. 自动建立云资源关联关系

---

## 6. 前端页面

| 页面 | 路由 | 功能 |
|------|------|------|
| AssetList | `/cmdb/assets/` | 资产列表（支持按类型、状态、位置、业务筛选） |
| AssetDetail | `/cmdb/assets/:id/` | 资产详情（基本信息、关联关系、变更历史） |
| AssetCreate | `/cmdb/assets/create/` | 创建资产 |
| LocationTree | `/cmdb/locations/` | 位置树管理（树形展示、拖拽调整） |
| BusinessTree | `/cmdb/business-tree/` | 服务树管理 |
| CloudAccounts | `/cmdb/cloud-accounts/` | 云账号配置 |
| TagManage | `/cmdb/tags/` | 标签管理 |

---

## 7. 与现有模块集成

| 现有模块 | 集成方式 |
|---------|---------|
| users.User | 操作用户、负责人 |
| monitor | 资产状态与监控告警联动 |
| tickets | 资产变更触发审批流 |

---

## 8. 实施范围（第一阶段）

### 8.1 核心功能
- Asset 统一资产模型 + CRUD
- AssetTypeDefinition 类型定义
- AssetChangeLog 变更审计
- Relationship 关系管理（runs_on/depends_on/connects_to）
- Tag / AssetTag 标签管理
- LocationNode 位置树 CRUD
- BusinessServiceNode 服务树 CRUD

### 8.2 自动纳管
- Agent 上报接口 `/assets/auto-discover/`
- CloudAccount 云账号配置
- CloudResourceMapping 映射规则
- AWS 适配器示例

### 8.3 后续扩展
- 其他云厂商适配器（阿里云、腾讯云）
- 完整服务树动态构建
- 资产变更比对视图
- 与监控/成本平台联动
