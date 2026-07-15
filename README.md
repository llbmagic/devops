# DevOps 一站式智能运维平台

基于 Django REST Framework + Vue.js 3 + ElementUI 的前后端分离运维平台。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Django 5 + djangorestframework + djangorestframework-simplejwt |
| 前端 | Vue 3 + TypeScript + ElementPlus + Pinia |
| 数据库 | MySQL 8.0 |
| 部署 | Docker Compose + nginx |

## 功能模块

- **CMDB** - 主机管理、业务线、环境、应用、集群、标签、应用依赖关系
- **CI/CD** - Jenkins 集成、流水线管理、构建触发
- **监控告警** - Prometheus 集成、告警规则、Alertmanager Webhook

## 快速启动（Docker）

### 前置条件

- Docker Desktop 已安装并运行
- 端口未占用：3306、8000、8080

### 启动步骤

```bash
# 1. 进入项目目录
cd /Users/lianglongbin/my_data/code/devops

# 2. 构建并启动所有服务
docker-compose up --build

# 3. 查看日志确认启动状态
# 看到以下日志表示启动成功：
# - "MySQL 已就绪"
# - "执行数据库迁移..."
# - Backend 和 Frontend 服务 Running
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:8080 |
| 后端 API | http://localhost:8000 |
| Django Admin | http://localhost:8000/admin/ |

### 创建管理员账号

```bash
# 进入 backend 容器
docker-compose exec backend bash

# 创建超级用户
python manage.py createsuperuser

# 按提示输入用户名、邮箱、密码
```

### 常用命令

```bash
# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up --build

# 查看运行中的容器
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
```

## 本地开发启动（可选）

### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库（修改 settings.py 中的 DATABASES）
# 确保 MySQL 服务运行中

# 执行迁移
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 项目结构

```
devops/
├── backend/              # Django REST Framework API
│   ├── apps/
│   │   ├── users/       # 用户认证、权限
│   │   ├── cmdb/        # 资产管理
│   │   ├── cicd/        # Jenkins 集成
│   │   └── monitor/     # Prometheus 监控
│   └── devops/          # Django 配置
├── frontend/            # Vue 3 前端
│   └── src/
│       ├── api/         # Axios 封装
│       ├── views/       # 页面组件
│       └── router/      # 路由配置
└── docker/              # Docker 部署配置
```

## 数据库连接信息

| 配置项 | 值 |
|--------|-----|
| 主机 | localhost 或 127.0.0.1 |
| 端口 | 3306 |
| 数据库 | devops_db |
| 用户名 | root |
| 密码 | devops123 |

## API 路由

| 前缀 | 模块 | 说明 |
|------|------|------|
| `/api/users/login/` | users | JWT 登录 |
| `/api/users/refresh/` | users | JWT 刷新 |
| `/api/users/users/` | users | 用户 CRUD |
| `/api/users/roles/` | users | 角色 CRUD |
| `/api/users/departments/` | users | 部门 CRUD |
| `/api/cmdb/business-lines/` | cmdb | 业务线 CRUD |
| `/api/cmdb/environments/` | cmdb | 环境 CRUD |
| `/api/cmdb/applications/` | cmdb | 应用 CRUD |
| `/api/cmdb/clusters/` | cmdb | 集群 CRUD |
| `/api/cmdb/tags/` | cmdb | 标签 CRUD |
| `/api/cmdb/hosts/` | cmdb | 主机 CRUD |
| `/api/cmdb/application-dependencies/` | cmdb | 应用依赖关系 CRUD |
| `/api/cicd/jenkins-instances/` | cicd | Jenkins 实例管理 |
| `/api/cicd/jobs/` | cicd | Jenkins Job CRUD |
| `/api/cicd/builds/` | cicd | 构建记录 |
| `/api/cicd/pipelines/` | cicd | 流水线 CRUD |
| `/api/monitor/prometheus-instances/` | monitor | Prometheus 实例管理 |
| `/api/monitor/alert-rules/` | monitor | 告警规则 CRUD |
| `/api/monitor/alerts/` | monitor | 告警记录 |

启动后访问：http://localhost:8000/admin/

或使用 DRF 提供的 API 浏览界面。
