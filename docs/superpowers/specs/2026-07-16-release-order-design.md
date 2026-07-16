# 发布审批模块设计方案

## 1. 概述

发布审批模块为 DevOps 平台提供标准化发布流程，支持参数校验、多级审批、定时/手动执行、状态回写和审计追溯。

**设计原则：**
- 平台负责发布单、参数校验、审批、审计、状态回写
- Jenkins 负责执行（调用 Ansible/kubectl/helm）
- 平台只保存任务模板与参数映射，不直接管理执行引擎

## 2. 架构分层

```
平台 ──────────────────────> Jenkins ──────────────────────> 集群
 │                              │
 ├── 发布单                      ├── 构建执行
 ├── 参数校验 (JSON Schema)      └── 状态回写
 ├── 多级审批
 ├── 定时/手动执行
 └── 审计日志
```

## 3. 数据模型

### 3.1 ReleaseOrder（发布单）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| title | CharField(200) | 发布标题 |
| description | TextField | 发布描述 |
| jenkins_job | ForeignKey | 关联的 Jenkins Job（创建时选择） |
| job_parameters | JSONField | 发布的参数字典值 |
| execute_mode | CharField | 执行模式：manual/scheduled |
| scheduled_time | DateTimeField | 定时发布时间（可选） |
| status | CharField | 状态 |
| current_step | IntegerField | 当前审批步骤 |
| applicant | ForeignKey | 申请人 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |
| closed_at | DateTimeField | 关闭时间 |

**状态流转：**
```
draft → pending → approved → executing → success/failed → closed
         ↓
      rejected → closed
```

### 3.2 ReleaseRecord（发布执行记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| release_order | ForeignKey | 关联的发布单 |
| build_record | ForeignKey | 关联的 Jenkins BuildRecord（可选） |
| executor | CharField(100) | 执行人 |
| result | CharField | 执行结果 |
| output | TextField | 执行输出摘要 |
| started_at | DateTimeField | 开始时间 |
| finished_at | DateTimeField | 结束时间 |

### 3.3 复用工单模块

- **ApprovalStep**：审批步骤
- **ApprovalRecord**：审批记录

## 4. API 端点

### 4.1 发布单 CRUD

```
POST   /api/cicd/release-orders/           # 创建发布单
GET    /api/cicd/release-orders/           # 列表（支持筛选）
GET    /api/cicd/release-orders/{id}/        # 详情
PATCH  /api/cicd/release-orders/{id}/        # 更新（仅草稿状态）
DELETE /api/cicd/release-orders/{id}/          # 删除（仅草稿状态）
```

### 4.2 审批流程

```
POST   /api/cicd/release-orders/{id}/submit/    # 提交审批
POST   /api/cicd/release-orders/{id}/approve/    # 审批通过
POST   /api/cicd/release-orders/{id}/reject/     # 审批拒绝
```

### 4.3 执行控制

```
POST   /api/cicd/release-orders/{id}/execute/    # 手动执行
POST   /api/cicd/release-orders/{id}/cancel/      # 取消发布
```

### 4.4 执行记录与 Webhook

```
GET    /api/cicd/release-orders/{id}/records/    # 执行记录列表
POST   /api/cicd/webhooks/jenkins/                 # Jenkins Webhook 回调
```

## 5. 工作流程

### 5.1 发布单生命周期

```
创建发布单（选择 Jenkins Job，填写参数）
    ↓
提交审批（选择审批人，进入 pending）
    ↓
多级审批（逐级通过或拒绝）
    ↓
审批通过 → 等待执行
    ↓
┌─────────────────────────────────────┐
│ 手动执行：用户点击"立即执行"           │
│ 定时执行：到达 scheduled_time 自动执行  │
└─────────────────────────────────────┘
    ↓
调用 Jenkins Job（携带参数）
    ↓
状态回写（轮询 + Webhook）
    ↓
发布成功/失败 → 记录 ReleaseRecord
```

### 5.2 状态回写机制

1. **轮询**：定时任务查询 Jenkins BuildRecord 状态
2. **Webhook**：Jenkins 调用 `/api/cicd/webhooks/jenkins/` 回调

## 6. 前端页面

| 页面 | 路由 | 功能 |
|------|------|------|
| ReleaseOrderList | /cicd/release-orders/ | 发布单列表（筛选：状态、时间范围） |
| ReleaseOrderCreate | /cicd/release-orders/create/ | 创建发布单（选择 Job、填写参数、选择审批人） |
| ReleaseOrderDetail | /cicd/release-orders/:id/ | 详情页（参数、审批历史、执行记录） |
| MyReleaseOrders | /cicd/release-orders/my/ | 我的待审批（审批人视角） |

## 7. 参数校验

### 7.1 JSON Schema 校验

创建发布单时，根据 Jenkins Job 定义的参数结构进行校验：

- 参数类型：string/number/boolean
- 必填参数：required 字段
- 格式校验：pattern（正则）、minLength/maxLength
- 数值范围：minimum/maximum

### 7.2 校验失败处理

返回 400 错误，包含详细的校验错误信息。

## 8. 与现有模块集成

| 现有模块 | 集成方式 |
|---------|---------|
| JenkinsJob | ForeignKey，发布时选择 |
| BuildRecord | ForeignKey，状态回写时关联 |
| ApprovalStep/ApprovalRecord | 复用审批逻辑 |
| User | 申请人、审批人、执行人 |

## 9. 定时执行实现

使用 Django Q 或 Celery 实现定时任务：

1. 每分钟扫描 `execute_mode=scheduled` 且 `scheduled_time<=now` 的发布单
2. 自动触发执行
3. 更新状态为 `executing`

## 10. 安全考虑

- 只有申请人可以提交、取消自己的发布单
- 只有当前审批步骤的审批人可以审批
- 执行时记录操作人
- 所有状态变更记录审计日志
