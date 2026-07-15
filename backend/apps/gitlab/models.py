"""GitLab 集成模块数据模型.

提供 GitLab 实例、代码仓库、合并请求的数据模型定义。
"""

import logging
from django.db import models

logger = logging.getLogger(__name__)


class GitLabInstance(models.Model):
    """GitLab 实例模型.

    存储 GitLab 服务器的连接信息，用于调用 GitLab API。
    支持 GitLab CE/EE 版本。

    属性:
        name: 实例名称，如"公司 GitLab"。
        url: GitLab 服务器地址，如 https://gitlab.example.com。
        access_token: GitLab Access Token，用于 API 认证。
        is_active: 是否启用。
        created_at: 创建时间。

    示例:
        >>> GitLabInstance.objects.create(
        ...     name='公司 GitLab',
        ...     url='https://gitlab.example.com',
        ...     access_token='glpat-xxxxx'
        ... )
    """

    name = models.CharField(
        max_length=100,
        verbose_name='实例名称',
        help_text='GitLab 实例的显示名称'
    )
    url = models.URLField(
        verbose_name='GitLab URL',
        help_text='GitLab 服务器地址，如 https://gitlab.example.com'
    )
    access_token = models.CharField(
        max_length=200,
        verbose_name='Access Token',
        help_text='GitLab Access Token，用于 API 认证'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='禁用后不会同步该实例的项目'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'gitlab_instance'。
        """
        db_table = 'gitlab_instance'
        verbose_name = 'GitLab 实例'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回实例名称."""
        return self.name


class Project(models.Model):
    """代码仓库模型.

    从 GitLab 实例同步的项目信息。

    属性:
        instance: 所属 GitLab 实例，外键关联。
        gitlab_id: GitLab 项目 ID。
        name: 项目名称。
        path_with_namespace: 完整路径，如 group/project。
        web_url: 项目 Web URL。
        default_branch: 默认分支。
        last_activity_at: 最后活动时间。

    示例:
        >>> instance = GitLabInstance.objects.first()
        >>> Project.objects.create(
        ...     instance=instance,
        ...     gitlab_id=123,
        ...     name='my-project',
        ...     path_with_namespace='group/my-project',
        ...     web_url='https://gitlab.example.com/group/my-project'
        ... )
    """

    instance = models.ForeignKey(
        GitLabInstance,
        on_delete=models.CASCADE,
        verbose_name='所属实例',
        help_text='项目所属的 GitLab 实例'
    )
    gitlab_id = models.IntegerField(
        verbose_name='GitLab ID',
        help_text='GitLab 项目 ID'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='项目名称',
        help_text='GitLab 项目名称'
    )
    path_with_namespace = models.CharField(
        max_length=500,
        verbose_name='完整路径',
        help_text='项目的完整路径，如 group/project'
    )
    web_url = models.URLField(
        verbose_name='项目URL',
        help_text='项目的 Web 地址'
    )
    default_branch = models.CharField(
        max_length=100,
        default='main',
        verbose_name='默认分支',
        help_text='项目的默认分支'
    )
    last_activity_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后活动',
        help_text='项目最后活动时间'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='同步时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'gitlab_project'。
        instance 和 gitlab_id 组合唯一。
        """
        db_table = 'gitlab_project'
        verbose_name = '代码仓库'
        verbose_name_plural = verbose_name
        unique_together = ['instance', 'gitlab_id']

    def __str__(self) -> str:
        """返回项目完整路径."""
        return self.path_with_namespace


class MergeRequest(models.Model):
    """合并请求模型.

    存储 MR 的基本信息，不存储完整的讨论和评论。

    属性:
        project: 所属项目，外键关联。
        gitlab_id: GitLab MR IID。
        title: MR 标题。
        source_branch: 源分支。
        target_branch: 目标分支。
        state: MR 状态（opened/closed/merged）。
        author: MR 作者。
        assignee: MR 负责人。
        review_status: 审批状态（pending/approved/rejected）。
        pipeline_status: CI 流水线状态（running/success/failed）。
        web_url: MR Web URL。
        created_at: 创建时间。
        updated_at: 更新时间。

    示例:
        >>> project = Project.objects.first()
        >>> MergeRequest.objects.create(
        ...     project=project,
        ...     gitlab_id=1,
        ...     title='Feature: 添加新功能',
        ...     source_branch='feature/new-feature',
        ...     target_branch='main',
        ...     state='opened',
        ...     author='developer'
        ... )
    """

    STATE_CHOICES = [
        ('opened', '开启'),
        ('closed', '关闭'),
        ('merged', '已合并'),
    ]
    REVIEW_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]
    PIPELINE_CHOICES = [
        ('running', '运行中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('canceled', '取消'),
        ('pending', '等待'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='merge_requests',
        verbose_name='所属项目',
        help_text='MR 所属的项目'
    )
    gitlab_id = models.IntegerField(
        verbose_name='GitLab IID',
        help_text='GitLab MR 的 IID'
    )
    title = models.CharField(
        max_length=500,
        verbose_name='标题',
        help_text='MR 的标题'
    )
    source_branch = models.CharField(
        max_length=200,
        verbose_name='源分支',
        help_text='MR 的源分支'
    )
    target_branch = models.CharField(
        max_length=200,
        verbose_name='目标分支',
        help_text='MR 的目标分支'
    )
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default='opened',
        verbose_name='状态',
        help_text='MR 状态：opened-开启，closed-关闭，merged-已合并'
    )
    author = models.CharField(
        max_length=100,
        verbose_name='作者',
        help_text='MR 作者的用户名'
    )
    assignee = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Assignee',
        help_text='MR 负责人'
    )
    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_CHOICES,
        default='pending',
        verbose_name='审批状态',
        help_text='审批状态：pending-待审批，approved-已批准，rejected-已拒绝'
    )
    pipeline_status = models.CharField(
        max_length=20,
        choices=PIPELINE_CHOICES,
        null=True,
        blank=True,
        verbose_name='流水线状态',
        help_text='CI 流水线状态'
    )
    web_url = models.URLField(
        verbose_name='MR URL',
        help_text='MR 的 Web 地址'
    )
    created_at = models.DateTimeField(
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'gitlab_merge_request'。
        project 和 gitlab_id 组合唯一，按更新时间倒序。
        """
        db_table = 'gitlab_merge_request'
        verbose_name = '合并请求'
        verbose_name_plural = verbose_name
        unique_together = ['project', 'gitlab_id']
        ordering = ['-updated_at']

    def __str__(self) -> str:
        """返回 MR 描述."""
        return f"{self.project.path_with_namespace}!{self.gitlab_id} {self.title}"
