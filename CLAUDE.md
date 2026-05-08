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
│   │   ├── cmdb/         # 资产管理（Host、BusinessLine、Tag）
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
| `/api/auth/login/` | users | JWT 登录（POST） |
| `/api/auth/refresh/` | users | JWT 刷新（POST） |
| `/api/users/users/` | users | 用户 CRUD |
| `/api/users/roles/` | users | 角色 CRUD |
| `/api/users/departments/` | users | 部门 CRUD |
| `/api/cmdb/hosts/` | cmdb | 主机 CRUD，支持按 `business_line`、`status` 筛选 |
| `/api/cmdb/business-lines/` | cmdb | 业务线 CRUD |
| `/api/cmdb/tags/` | cmdb | 标签 CRUD |
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
