"""Users 模块序列化器.

提供用户认证、权限管理相关模型的序列化器，用于 API 数据的序列化和反序列化。

主要序列化器:
    - PermissionSerializer: 权限序列化器（只读）
    - RoleSerializer: 角色序列化器，包含权限详情
    - DepartmentSerializer: 部门序列化器
    - UserSerializer: 用户序列化器，包含角色和部门信息
    - UserCreateSerializer: 用户创建序列化器，支持密码设置

使用示例:
    >>> from apps.users.serializers import UserSerializer
    >>> from apps.users.models import User
    >>> user = User.objects.first()
    >>> serializer = UserSerializer(user)
    >>> print(serializer.data)
"""

import logging
from typing import Optional

from rest_framework import serializers
from .models import User, Role, Permission, Department

# 模块级日志记录器
logger = logging.getLogger(__name__)


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器.

    用于序列化权限模型，包含权限名称、代码和所属模块。
    """

    class Meta:
        """序列化器元数据.

        属性:
            model: 对应的模型类。
            fields: 序列化的字段，'__all__' 表示所有字段。
        """
        model = Permission
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器.

    序列化角色模型，包含角色关联的权限详情列表。

    示例:
        >>> serializer = RoleSerializer(role)
        >>> serializer.data
        {'id': 1, 'name': '管理员', 'permissions': [...], 'description': '...'}
    """

    permissions = PermissionSerializer(
        many=True,
        read_only=True,
        help_text='角色拥有的权限列表'
    )

    class Meta:
        """序列化器元数据."""
        model = Role
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器.

    序列化部门模型，支持层级结构的展示。

    示例:
        >>> serializer = DepartmentSerializer(department)
        >>> serializer.data
        {'id': 1, 'name': '技术部', 'parent': None}
    """

    class Meta:
        """序列化器元数据."""
        model = Department
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器.

    序列化用户模型，包含用户名、邮箱、手机号、部门、角色等信息。
    密码字段不包含在序列化结果中（只读）。

    新增字段:
        roles: 角色详情列表（只读）
        department_name: 部门名称（只读）

    示例:
        >>> serializer = UserSerializer(user)
        >>> serializer.data
        {'id': 1, 'username': 'admin', 'email': 'admin@example.com',
         'roles': [...], 'department_name': '技术部', ...}
    """

    roles = RoleSerializer(
        many=True,
        read_only=True,
        help_text='用户拥有的角色列表'
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
        help_text='所属部门名称'
    )

    class Meta:
        """序列化器元数据.

        密码字段为只写，不出现在序列化结果中。
        """
        model = User
        fields = [
            'id', 'username', 'email', 'phone',
            'department', 'department_name', 'roles',
            'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器.

    用于创建新用户，支持设置密码。密码字段为必填，最短 6 个字符。

    属性:
        password: 密码字段，写入时必须，值会被哈希处理。

    示例:
        >>> data = {'username': 'newuser', 'password': 'password123', 'email': 'new@example.com'}
        >>> serializer = UserCreateSerializer(data=data)
        >>> if serializer.is_valid():
        ...     user = serializer.save()
    """

    password = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text='用户密码，最短 6 个字符'
    )

    class Meta:
        """序列化器元数据."""
        model = User
        fields = [
            'id', 'username', 'password', 'email',
            'phone', 'department', 'is_active'
        ]

    def create(self, validated_data: dict) -> User:
        """创建用户实例.

        从验证后的数据中取出密码，使用 set_password() 加密后保存。

        Args:
            validated_data: 验证后的数据字典，包含用户信息。

        Returns:
            创建的用户实例。
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        logger.info(f"创建新用户: {user.username}")
        return user
