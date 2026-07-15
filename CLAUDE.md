# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码仓库工作时提供指导。

## 项目概述

DevOps 是一站式智能运维平台，包含 CMDB 资产管理、CI/CD 流水线（Jenkins 集成）和统一监控告警（Prometheus）。基于 Django REST Framework + Vue.js 3 + ElementUI 构建。

## 架构

```
devops/
├── backend/              # Django REST Framework API
│   ├── apps/
│   │   ├── users/        # JWT 认证、RBAC（User、Role、Permission、Department）
│   │   ├── cmdb/         # 资产管理（Host、BusinessLine、Tag、Environment、Application、Cluster、ApplicationDependency）
│   │   ├── cicd/         # Jenkins 集成（JenkinsInstance、JenkinsJob、BuildRecord、Pipeline）
│   │   └── monitor/      # Prometheus 集成（PrometheusInstance、AlertRule、AlertRecord、MonitorTarget）
│   └── devops/           # Django 项目配置
├── frontend/             # Vue 3 + ElementUI 单页应用
│   └── src/
│       ├── api/          # Axios 封装，含 JWT 拦截器
│       ├── views/        # 页面组件（共 12 个）
│       └── router/       # Vue Router 配置
└── docker/               # Docker Compose + Dockerfiles
```

## 常用命令

### 后端（Django）

```bash
cd backend
source venv/bin/activate        # 激活虚拟环境
pip install -r requirements.txt  # 安装依赖
python manage.py migrate         # 执行数据库迁移
python manage.py createsuperuser # 创建管理员用户
python manage.py runserver      # 开发服务器 http://localhost:8000
```

### 前端（Vue）

```bash
cd frontend
npm install                     # 安装依赖
npm run dev                     # 开发服务器 http://localhost:5173
npm run build                   # 生产环境构建
npm run type-check             # TypeScript 类型检查
```

### Docker

```bash
docker-compose up --build       # 构建并启动所有服务
```

## API 路由

| 前缀 | 模块 | 说明 |
|------|------|------|
| `/api/users/login/` | users | JWT 登录（POST） |
| `/api/users/refresh/` | users | JWT 刷新（POST） |
| `/api/users/users/` | users | 用户 CRUD |
| `/api/users/roles/` | users | 角色 CRUD |
| `/api/users/departments/` | users | 部门 CRUD |
| `/api/cmdb/business-lines/` | cmdb | 业务线 CRUD |
| `/api/cmdb/environments/` | cmdb | 环境 CRUD（dev/test/staging/prod） |
| `/api/cmdb/applications/` | cmdb | 应用 CRUD，关联业务线 |
| `/api/cmdb/clusters/` | cmdb | 集群 CRUD，关联应用+环境 |
| `/api/cmdb/tags/` | cmdb | 标签 CRUD |
| `/api/cmdb/hosts/` | cmdb | 主机 CRUD，支持按 `business_line`、`cluster`、`status` 筛选 |
| `/api/cmdb/application-dependencies/` | cmdb | 应用依赖关系 CRUD |
| `/api/cicd/jenkins-instances/` | cicd | Jenkins 实例管理 |
| `/api/cicd/jobs/` | cicd | Jenkins Job CRUD，`build` 操作触发 Jenkins 构建 |
| `/api/cicd/builds/` | cicd | 构建记录（只读） |
| `/api/cicd/pipelines/` | cicd | 流水线 CRUD |
| `/api/monitor/prometheus-instances/` | monitor | Prometheus 实例管理 |
| `/api/monitor/alert-rules/` | monitor | 告警规则 CRUD |
| `/api/monitor/alerts/` | monitor | 告警记录，`acknowledge` 操作确认告警 |
| `/api/monitor/webhooks/alertmanager/` | monitor | Alertmanager Webhook 接收端点 |

## 关键实现说明

- **认证**：使用 `djangorestframework-simplejwt`，自定义用户模型（`AUTH_USER_MODEL = 'users.User'`）
- **数据库**：通过 pymysql 连接 MySQL（macOS 兼容），生产环境需在 settings.py 中更新数据库配置
- **CORS**：已配置允许 `localhost:5173`（Vite）和 `localhost:8080`（nginx）
- **Jenkins 集成**：从 Jenkins 实例同步 Job，通过 Jenkins API 触发构建
- **Prometheus 集成**：查询和目标端点代理到 Prometheus API；Alertmanager 发送 Webhook 到 `/api/monitor/webhooks/alertmanager/`
- **前端 API 客户端**：`src/api/index.ts` 中的 Axios 实例自动附加 JWT Token，并在 401 时重定向到登录页

## 技术栈

- **后端**：Django 5+、djangorestframework、djangorestframework-simplejwt、pymysql、requests
- **前端**：Vue 3（组合式 API）、TypeScript、ElementPlus、Pinia、Vue Router 4、Axios
- **DevOps**：Docker、Docker Compose、nginx


## 开发规范

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- 实现前明确假设，不确定时主动询问
- 存在多种解释时列出对比，不自行选择
- 存在更简单方案时提出
- 不清晰时停止，明确指出疑问

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- 不添加需求之外的特性
- 不为单次使用的代码创建抽象
- 不添加未请求的"灵活性"或"可配置性"
- 不为不可能发生的场景添加错误处理

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- 编辑现有代码时不"改进"相邻代码、注释或格式
- 不重构未损坏的内容
- 遵循现有代码风格
- 变更产生的孤儿代码需清理

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

- 多步骤任务需明确执行计划
- 每步验证后再进行下一步

---

## Python 开发规则

### 类型提示

- **必须**: 所有函数必须有输入参数和返回值的类型注解
- 使用标准 `typing` 模块 (`Optional`, `Union`, `Callable` 等)

### 日志管理

- 使用 `logging` 替代 `print`
- 主入口设置全局日志格式: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- 读取环境变量 `LOG_LEVEL` 设置全局日志等级
- 各模块创建模块级别 logger

```python
import logging
logger = logging.getLogger(__name__)
```

### 代码规范

- 遵循 Google Python Style Guide
- 所有公开子模块显式导入父模块命名空间
- 模块 docstring 第一句明确模块核心用途
- 所有公开 API 必须补全参数说明
- 方法调用使用显式参数签名


### 其他

- 调用外部依赖时必须有健壮的错误处理
- 代码示例放在 `if __name__ == "__main__":` 中
- 新增封装接口时，必须提供示例代码，且接口信息必须添加到 API 文档中
