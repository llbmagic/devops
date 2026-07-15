"""Users 模块视图集.

提供用户认证、权限管理相关的 ViewSet，实现用户、角色、权限、部门的管理功能。

主要功能:
    - 部门管理（CRUD，支持层级结构）
    - 权限管理（只读，查看所有权限列表）
    - 角色管理（CRUD，支持分配权限）
    - 用户管理（CRUD，获取当前用户信息）
    - JWT 认证（登录、刷新 Token）

API 路由:
    - /api/users/login/ - JWT 登录（POST）
    - /api/users/refresh/ - JWT 刷新（POST）
    - /api/users/departments/ - 部门 CRUD
    - /api/users/permissions/ - 权限列表（只读）
    - /api/users/roles/ - 角色 CRUD
    - /api/users/roles/{id}/assign_permissions/ - 分配权限
    - /api/users/users/ - 用户 CRUD
    - /api/users/users/me/ - 获取当前用户信息

认证说明:
    - 登录接口允许匿名访问（AllowAny）
    - 其他接口需要登录认证（IsAuthenticated）
"""

import logging
from typing import Optional

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Role, Permission, Department
from .serializers import (
    UserSerializer, UserCreateSerializer,
    RoleSerializer, PermissionSerializer, DepartmentSerializer
)

# 模块级日志记录器
logger = logging.getLogger(__name__)


class DepartmentViewSet(viewsets.ModelViewSet):
    """部门视图集.

    管理部门组织架构，支持层级结构。顶级部门的 parent 为空。

    路由:
        GET /api/users/departments/ - 获取部门列表
        POST /api/users/departments/ - 创建新部门
        GET /api/users/departments/{id}/ - 获取部门详情
        PUT /api/users/departments/{id}/ - 更新部门
        DELETE /api/users/departments/{id}/ - 删除部门
    """

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """权限视图集.

    提供权限的只读访问，用于查看所有可用权限及其分组。

    路由:
        GET /api/users/permissions/ - 获取权限列表
        GET /api/users/permissions/{id}/ - 获取权限详情
    """

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]


class RoleViewSet(viewsets.ModelViewSet):
    """角色视图集.

    管理角色，包括创建、编辑、删除、分配权限等操作。

    路由:
        GET /api/users/roles/ - 获取角色列表
        POST /api/users/roles/ - 创建新角色
        GET /api/users/roles/{id}/ - 获取角色详情
        PUT /api/users/roles/{id}/ - 更新角色
        DELETE /api/users/roles/{id}/ - 删除角色
        POST /api/users/roles/{id}/assign_permissions/ - 为角色分配权限
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def assign_permissions(self, request: Request, pk: Optional[str] = None) -> Response:
        """为角色分配权限.

        替换角色的权限列表为指定的新权限 ID 列表。

        Args:
            request: HTTP 请求对象，包含 permission_ids 列表。
            pk: 角色的主键 ID。

        Returns:
            包含状态信息的响应对象。

        示例:
            POST /api/users/roles/1/assign_permissions/
            Body: {"permission_ids": [1, 2, 3]}
        """
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        role.permissions.set(permission_ids)
        logger.info(f"为角色 {role.name} 分配了 {len(permission_ids)} 个权限")
        return Response({'status': 'ok'})


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集.

    管理用户，包括创建、编辑、删除、查看个人信息等操作。
    创建用户时使用 UserCreateSerializer，其他操作使用 UserSerializer。

    路由:
        GET /api/users/users/ - 获取用户列表
        POST /api/users/users/ - 创建新用户
        GET /api/users/users/{id}/ - 获取用户详情
        PUT /api/users/users/{id}/ - 更新用户
        DELETE /api/users/users/{id}/ - 删除用户
        GET /api/users/users/me/ - 获取当前登录用户信息
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) -> type:
        """根据操作类型返回不同的序列化器.

        创建用户时使用 UserCreateSerializer（支持密码设置），
        其他操作使用 UserSerializer。

        Returns:
            序列化器类。
        """
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request: Request) -> Response:
        """获取当前登录用户信息.

        返回当前认证用户的所有信息，包括角色和部门。

        Args:
            request: HTTP 请求对象，已认证用户。

        Returns:
            当前用户的序列化数据。

        示例:
            GET /api/users/users/me/
            Response: {"id": 1, "username": "admin", "roles": [...], ...}
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
