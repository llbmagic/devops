"""Users 模块数据模型.

提供用户认证、权限管理相关的数据模型，包括用户、角色、权限、部门等。

数据模型:
    - Department: 部门组织架构，支持层级结构
    - User: 自定义用户模型，扩展 Django 内置用户
    - Role: 角色，用于权限分组
    - Permission: 权限，细粒度访问控制

典型使用场景:
    - 用户登录认证（JWT）
    - 用户管理（CRUD）
    - 角色权限分配
    - 部门组织架构管理

权限控制:
    - 用户可以属于多个角色
    - 角色可以分配多个权限
    - 权限按模块分组（如 cmdb、cicd、monitor）

示例:
    >>> from apps.users.models import User, Role
    >>> user = User.objects.get(username='admin')
    >>> print(user.roles.all())
"""

import logging
from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models

# 模块级日志记录器
logger = logging.getLogger(__name__)


class Department(models.Model):
    """部门模型.

    支持层级结构的部门组织架构，通过 parent 自关联实现多级部门。
    用户关联部门后，可以按部门进行数据权限隔离。

    属性:
        name: 部门名称，最长 100 个字符。
        parent: 上级部门，自关联外键，可为空（顶级部门）。

    示例:
        >>> # 创建顶级部门
        >>> tech_dept = Department.objects.create(name='技术部')
        >>> # 创建子部门
        >>> backend_dept = Department.objects.create(name='后端组', parent=tech_dept)
    """

    name = models.CharField(
        max_length=100,
        verbose_name='部门名称',
        help_text='部门的显示名称'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='上级部门',
        help_text='上级部门，用于构建部门层级'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'department'。
        """
        db_table = 'department'
        verbose_name = '部门'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回部门的字符串表示.

        Returns:
            部门名称。
        """
        return self.name


class User(AbstractUser):
    """用户模型.

    扩展 Django 内置用户模型，添加手机号、部门、角色等字段。
    支持多角色分配和灵活的组织架构关联。

    属性:
        phone: 手机号，可选，最长 20 个字符。
        department: 所属部门，外键关联，可为空。
        roles: 用户角色，多对多关联。
        groups: 继承自 AbstractUser，保持兼容。
        user_permissions: 继承自 AbstractUser，保持兼容。

    注意:
        - 使用 AUTH_USER_MODEL = 'users.User' 配置
        - 密码通过 set_password() 设置，使用 Django 默认加密

    示例:
        >>> from apps.users.models import User, Department
        >>> dept = Department.objects.get(name='技术部')
        >>> user = User.objects.create_user(
        ...     username='zhangsan',
        ...     password='password123',
        ...     email='zhangsan@example.com',
        ...     phone='13800138000',
        ...     department=dept
        ... )
    """

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='手机号',
        help_text='用户手机号码'
    )
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='部门',
        help_text='用户所属部门'
    )
    roles = models.ManyToManyField(
        'Role',
        blank=True,
        verbose_name='角色',
        help_text='用户拥有的角色列表'
    )
    # 保持与 AbstractUser 的兼容性
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='users_groups',
        related_query_name='users_group',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='users_permissions',
        related_query_name='users_permission',
    )

    class Meta:
        """模型元数据.

        数据库表名为 'user'。
        """
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Role(models.Model):
    """角色模型.

    角色是权限的容器，用于批量分配权限给用户。
    用户拥有角色后，即拥有该角色下的所有权限。

    属性:
        name: 角色名称，唯一，最长 50 个字符。
        permissions: 角色拥有的权限列表，多对多关联。
        description: 角色描述，可选，最长 200 个字符。

    示例:
        >>> from apps.users.models import Role, Permission
        >>> admin_role = Role.objects.create(name='管理员', description='系统管理员')
        >>> # 分配权限
        >>> perms = Permission.objects.filter(module='users')
        >>> admin_role.permissions.set(perms)
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='角色名称',
        help_text='角色的唯一名称'
    )
    permissions = models.ManyToManyField(
        'Permission',
        blank=True,
        verbose_name='权限',
        help_text='角色拥有的权限列表'
    )
    description = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='描述',
        help_text='角色的详细描述'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'role'。
        """
        db_table = 'role'
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回角色的字符串表示.

        Returns:
            角色名称。
        """
        return self.name


class Permission(models.Model):
    """权限模型.

    权限是访问控制的最小单元，按模块分组。
    权限代码（codename）用于程序中鉴权，名称用于展示。

    属性:
        name: 权限名称，唯一，最长 50 个字符，用于展示。
        codename: 权限代码，唯一，最长 100 个字符，用于程序鉴权。
        module: 所属模块，最长 50 个字符，如 users、cmdb、cicd。

    注意:
        - codename 格式建议：app_name.action（如 user.create）
        - module 用于按模块分组展示权限

    示例:
        >>> Permission.objects.create(
        ...     name='用户创建',
        ...     codename='users.user.create',
        ...     module='users'
        ... )
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='权限名称',
        help_text='权限的显示名称，如"用户创建"'
    )
    codename = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='权限编码',
        help_text='权限的唯一代码，如 users.user.create'
    )
    module = models.CharField(
        max_length=50,
        verbose_name='所属模块',
        help_text='权限所属模块，如 users、cmdb、cicd'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'permission'。
        """
        db_table = 'permission'
        verbose_name = '权限'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回权限的字符串表示.

        Returns:
            权限名称。
        """
        return self.name
