from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name='部门名称')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='上级部门')

    class Meta:
        db_table = 'department'
        verbose_name = '部门'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class User(AbstractUser):
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='手机号')
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL, verbose_name='部门')
    roles = models.ManyToManyField('Role', blank=True, verbose_name='角色')

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
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='角色名称')
    permissions = models.ManyToManyField('Permission', blank=True, verbose_name='权限')
    description = models.CharField(max_length=200, null=True, blank=True, verbose_name='描述')

    class Meta:
        db_table = 'role'
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Permission(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='权限名称')
    codename = models.CharField(max_length=100, unique=True, verbose_name='权限编码')
    module = models.CharField(max_length=50, verbose_name='所属模块')

    class Meta:
        db_table = 'permission'
        verbose_name = '权限'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name