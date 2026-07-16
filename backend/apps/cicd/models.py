"""CI/CD 模块数据模型.

提供 Jenkins 集成相关的数据模型，包括 Jenkins 实例、Job、构建记录和流水线等。

数据模型:
    - JenkinsInstance: Jenkins 服务器实例配置
    - JenkinsJob: 从 Jenkins 同步的 Job 信息
    - BuildRecord: 构建历史记录
    - Pipeline: 部署流水线配置

典型使用场景:
    - 添加公司 Jenkins 服务器到平台
    - 同步 Jenkins Job 到平台统一管理
    - 记录每次构建的详细信息
    - 配置流水线关联 Job 和目标主机

示例:
    >>> from apps.cicd.models import JenkinsInstance, JenkinsJob
    >>> instance = JenkinsInstance.objects.create(
    ...     name='Jenkins主服务器',
    ...     url='http://jenkins.example.com',
    ...     username='admin',
    ...     api_token='your-api-token'
    ... )
"""

import logging
from django.db import models

# 模块级日志记录器
logger = logging.getLogger(__name__)


class JenkinsInstance(models.Model):
    """Jenkins 实例模型.

    存储 Jenkins 服务器的连接信息，用于调用 Jenkins API。

    属性:
        name: 实例名称，最长 100 个字符。
        url: Jenkins 服务器地址，必须是有效的 URL 格式。
        username: Jenkins 用户名，用于 API 认证。
        api_token: Jenkins API Token（可从用户设置页面获取）。
        is_active: 是否启用，禁用后不会同步该实例的 Job。

    示例:
        >>> JenkinsInstance.objects.create(
        ...     name='Jenkins主服务器',
        ...     url='http://jenkins.example.com',
        ...     username='admin',
        ...     api_token='your-api-token'
        ... )
    """

    name = models.CharField(
        max_length=100,
        verbose_name='实例名称',
        help_text='Jenkins 实例的显示名称'
    )
    url = models.URLField(
        verbose_name='Jenkins URL',
        help_text='Jenkins 服务器地址，如 http://jenkins.example.com'
    )
    username = models.CharField(
        max_length=100,
        verbose_name='用户名',
        help_text='Jenkins 用户名'
    )
    api_token = models.CharField(
        max_length=200,
        verbose_name='API Token',
        help_text='Jenkins API Token'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='禁用后不会同步该实例的 Job'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'jenkins_instance'。
        """
        db_table = 'jenkins_instance'
        verbose_name = 'Jenkins 实例'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回实例的字符串表示.

        Returns:
            实例名称。
        """
        return self.name


class JenkinsJob(models.Model):
    """Jenkins Job 模型.

    从 Jenkins 实例同步的 Job 信息，包括名称、URL 和最新构建状态。

    属性:
        instance: 所属 Jenkins 实例，外键关联。
        name: Job 名称，最长 200 个字符。
        job_url: Job 的 URL 地址，可选。
        last_build_number: 最新构建号，默认为 0。
        last_build_status: 最新构建状态，可选值包括 success/failure/running/pending。
        last_build_time: 最新构建时间，可选。

    示例:
        >>> from apps.cicd.models import JenkinsInstance
        >>> instance = JenkinsInstance.objects.first()
        >>> JenkinsJob.objects.create(
        ...     instance=instance,
        ...     name='my-project-build',
        ...     job_url='http://jenkins.example.com/job/my-project-build'
        ... )
    """

    INSTANCE_TYPE_CHOICES = [
        ('jenkins', 'Jenkins'),
    ]

    instance = models.ForeignKey(
        JenkinsInstance,
        on_delete=models.CASCADE,
        verbose_name='所属实例',
        help_text='Job 所属的 Jenkins 实例'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Job 名称',
        help_text='Jenkins Job 的名称'
    )
    job_url = models.URLField(
        verbose_name='Job URL',
        blank=True,
        help_text='Job 的 URL 地址'
    )
    last_build_number = models.IntegerField(
        default=0,
        verbose_name='最后构建号',
        help_text='最新一次构建的编号'
    )
    last_build_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='最后构建状态',
        help_text='最新构建的状态，如 success/failure/running'
    )
    last_build_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后构建时间',
        help_text='最新构建的开始时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'jenkins_job'。
        """
        db_table = 'jenkins_job'
        verbose_name = 'Jenkins Job'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回 Job 的字符串表示.

        Returns:
            格式为"实例名/Job名"的字符串。
        """
        return f"{self.instance.name}/{self.name}"


class BuildRecord(models.Model):
    """构建记录模型.

    记录每次 Jenkins 构建的详细信息，用于追溯和统计。

    属性:
        job: 关联的 Jenkins Job，外键关联。
        build_number: 构建号，对应 Jenkins 中的构建编号。
        status: 构建状态，可选值：pending/running/success/failure/aborted。
        duration: 构建持续时间（秒），可选。
        executor: 执行人，即触发构建的用户。
        commit_id: 提交 ID（Git commit SHA），可选。
        log_url: 构建日志 URL，可选。
        started_at: 构建开始时间，自动设置。
        finished_at: 构建结束时间，可选。

    示例:
        >>> from apps.cicd.models import JenkinsJob
        >>> job = JenkinsJob.objects.first()
        >>> BuildRecord.objects.create(
        ...     job=job,
        ...     build_number=1,
        ...     status='success',
        ...     executor='admin'
        ... )
    """

    STATUS_CHOICES = [
        ('pending', '排队中'),
        ('running', '运行中'),
        ('success', '成功'),
        ('failure', '失败'),
        ('aborted', '中止'),
    ]

    job = models.ForeignKey(
        JenkinsJob,
        on_delete=models.CASCADE,
        related_name='builds',
        verbose_name='Job',
        help_text='关联的 Jenkins Job'
    )
    build_number = models.IntegerField(
        verbose_name='构建号',
        help_text='Jenkins 构建编号'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态',
        help_text='构建状态：pending-排队中，running-运行中，success-成功，failure-失败，aborted-中止'
    )
    duration = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='持续时间(秒)',
        help_text='构建持续时间，单位秒'
    )
    executor = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='执行人',
        help_text='触发构建的用户'
    )
    commit_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='提交ID',
        help_text='Git 提交 ID'
    )
    log_url = models.URLField(
        null=True,
        blank=True,
        verbose_name='日志URL',
        help_text='构建日志的 URL'
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='开始时间',
        help_text='构建开始时间，自动记录'
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='结束时间',
        help_text='构建结束时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'build_record'，按开始时间倒序排列。
        """
        db_table = 'build_record'
        verbose_name = '构建记录'
        verbose_name_plural = verbose_name
        ordering = ['-started_at']

    def __str__(self) -> str:
        """返回构建记录的字符串表示.

        Returns:
            格式为"Job名 #构建号"的字符串。
        """
        return f"{self.job.name} #{self.build_number}"


class Pipeline(models.Model):
    """流水线模型.

    将 Jenkins Job 与目标主机关联，支持一键部署到多台主机。

    属性:
        name: 流水线名称，最长 100 个字符。
        job: 关联的 Jenkins Job，外键关联。
        target_hosts: 目标主机列表，多对多关联。
        description: 流水线描述，可选。
        created_at: 创建时间，自动设置。

    示例:
        >>> from apps.cicd.models import JenkinsJob
        >>> from apps.cmdb.models import Host
        >>> job = JenkinsJob.objects.first()
        >>> hosts = Host.objects.all()[:3]
        >>> pipeline = Pipeline.objects.create(
        ...     name='用户服务部署流水线',
        ...     job=job
        ... )
        >>> pipeline.target_hosts.set(hosts)
    """

    name = models.CharField(
        max_length=100,
        verbose_name='流水线名称',
        help_text='流水线的显示名称'
    )
    job = models.ForeignKey(
        JenkinsJob,
        on_delete=models.CASCADE,
        verbose_name='关联 Job',
        help_text='流水线关联的 Jenkins Job'
    )
    target_hosts = models.ManyToManyField(
        'cmdb.Host',
        blank=True,
        verbose_name='目标主机',
        help_text='流水线部署的目标主机列表'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='描述',
        help_text='流水线的详细描述'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'pipeline'。
        """
        db_table = 'pipeline'
        verbose_name = '流水线'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回流水线的字符串表示.

        Returns:
            流水线名称。
        """
        return self.name


class ReleaseOrder(models.Model):
    """发布单模型.

    用于管理代码发布审批流程，包括参数校验、多级审批、定时/手动执行。

    属性:
        title: 发布标题。
        description: 发布描述。
        jenkins_job: 关联的 Jenkins Job，外键关联。
        job_parameters: 发布的参数字典值（JSON 格式）。
        execute_mode: 执行模式，manual-手动执行，scheduled-定时执行。
        scheduled_time: 定时发布时间（可选）。
        status: 发布单状态。
        current_step: 当前审批步骤。
        applicant: 申请人，外键关联用户。
        created_at: 创建时间。
        updated_at: 更新时间。
        closed_at: 关闭时间。

    状态流转:
        draft -> pending -> approved -> executing -> success/failed -> closed
            ↓
        rejected -> closed

    示例:
        >>> job = JenkinsJob.objects.first()
        >>> ReleaseOrder.objects.create(
        ...     title='v2.1.0 版本发布',
        ...     jenkins_job=job,
        ...     job_parameters={'version': '2.1.0', 'env': 'prod'},
        ...     execute_mode='manual',
        ...     applicant=user
        ... )
    """

    EXECUTE_MODE_CHOICES = [
        ('manual', '手动执行'),
        ('scheduled', '定时执行'),
    ]
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('executing', '执行中'),
        ('success', '执行成功'),
        ('failed', '执行失败'),
        ('closed', '已关闭'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name='发布标题',
        help_text='发布单的简要标题'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='发布描述',
        help_text='发布的详细描述'
    )
    jenkins_job = models.ForeignKey(
        JenkinsJob,
        on_delete=models.PROTECT,
        verbose_name='Jenkins Job',
        help_text='关联的 Jenkins Job'
    )
    job_parameters = models.JSONField(
        default=dict,
        verbose_name='发布参数',
        help_text='发布的参数字典值'
    )
    execute_mode = models.CharField(
        max_length=20,
        choices=EXECUTE_MODE_CHOICES,
        default='manual',
        verbose_name='执行模式',
        help_text='manual-手动执行，scheduled-定时执行'
    )
    scheduled_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='定时发布时间',
        help_text='定时执行的发布时间'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态',
        help_text='发布单状态'
    )
    current_step = models.IntegerField(
        default=0,
        verbose_name='当前步骤',
        help_text='当前审批步骤，从0开始'
    )
    applicant = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='release_orders',
        verbose_name='申请人',
        help_text='提交该发布单的用户'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='关闭时间',
        help_text='发布单关闭时间'
    )

    class Meta:
        db_table = 'release_order'
        verbose_name = '发布单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title


class ReleaseRecord(models.Model):
    """发布执行记录模型.

    记录每次发布的执行信息，用于审计追溯。

    属性:
        release_order: 关联的发布单，外键关联。
        build_record: 关联的 Jenkins BuildRecord，外键关联（可选）。
        executor: 执行人。
        result: 执行结果。
        output: 执行输出摘要。
        started_at: 开始时间。
        finished_at: 结束时间。

    示例:
        >>> order = ReleaseOrder.objects.first()
        >>> ReleaseRecord.objects.create(
        ...     release_order=order,
        ...     executor='admin',
        ...     result='success'
        ... )
    """

    RESULT_CHOICES = [
        ('success', '成功'),
        ('failure', '失败'),
        ('aborted', '中止'),
    ]

    release_order = models.ForeignKey(
        ReleaseOrder,
        on_delete=models.CASCADE,
        related_name='release_records',
        verbose_name='发布单',
        help_text='关联的发布单'
    )
    build_record = models.ForeignKey(
        BuildRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='构建记录',
        help_text='关联的 Jenkins BuildRecord'
    )
    executor = models.CharField(
        max_length=100,
        verbose_name='执行人',
        help_text='执行发布单的用户'
    )
    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        null=True,
        blank=True,
        verbose_name='执行结果',
        help_text='执行结果'
    )
    output = models.TextField(
        null=True,
        blank=True,
        verbose_name='执行输出',
        help_text='执行输出摘要'
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='开始时间'
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='结束时间',
        help_text='执行结束时间'
    )

    class Meta:
        db_table = 'release_record'
        verbose_name = '发布执行记录'
        verbose_name_plural = verbose_name
        ordering = ['-started_at']

    def __str__(self) -> str:
        return f"{self.release_order.title} - {self.result}"
