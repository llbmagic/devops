"""Users 模块.

提供用户认证、权限管理相关的功能，包括用户、角色、权限、部门等模型。

公开子模块:
    - models: User, Role, Permission, Department 模型定义
    - serializers: 各模型的序列化器
    - views: REST API 视图集
    - urls: 路由配置

典型使用场景:
    - 用户登录认证（JWT Token）
    - 用户管理（CRUD）
    - 角色权限管理
    - 部门组织架构管理

示例:
    >>> from apps.users.models import User
    >>> from apps.users.serializers import UserSerializer
"""

# 显式导出公开子模块（延迟导入，避免 AppRegistryNotReady）
__all__ = [
    'Department',
    'Permission',
    'Role',
    'User',
    'DepartmentSerializer',
    'PermissionSerializer',
    'RoleSerializer',
    'UserSerializer',
    'UserCreateSerializer',
    'DepartmentViewSet',
    'RoleViewSet',
    'UserViewSet',
]
