"""工单审批模块数据模型.

提供工单模板、工单、审批步骤、审批记录的数据模型定义。
"""

import logging
from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


class TicketTemplate(models.Model):
    """工单模板模型.

    定义工单的类型和默认的审批流程。

    属性:
        name: 模板名称，如"服务器申请"、"权限申请"。
        code: 模板代码，唯一标识。
        description: 模板描述。
        approvers: 默认审批人列表（逗号分隔的用户名）。
        approval_steps: 审批步骤数，默认1。
        variables: 工单变量定义（JSON 格式）。
        is_active: 是否启用。
        created_at: 创建时间。

    示例:
        >>> TicketTemplate.objects.create(
        ...     name='服务器申请',
        ...     code='server_request',
        ...     approvers='admin,manager',
        ...     approval_steps=2
        ... )
    """

    name = models.CharField(
        max_length=100,
        verbose_name='模板名称',
        help_text='工单模板的显示名称'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='模板代码',
        help_text='唯一标识代码，如 server_request'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='描述',
        help_text='模板的详细描述'
    )
    approvers = models.TextField(
        null=True,
        blank=True,
        verbose_name='默认审批人',
        help_text='默认审批人用户名列表，逗号分隔'
    )
    approval_steps = models.IntegerField(
        default=1,
        verbose_name='审批步骤数',
        help_text='审批流程的步骤数量'
    )
    variables = models.TextField(
        null=True,
        blank=True,
        verbose_name='变量定义',
        help_text='JSON 格式的工单变量定义'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='禁用后不能创建该类型的工单'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'ticket_template'。
        """
        db_table = 'ticket_template'
        verbose_name = '工单模板'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回模板名称."""
        return self.name


class Ticket(models.Model):
    """工单实例模型.

    代表用户提交的具体工单。

    属性:
        title: 工单标题。
        template: 所属模板，外键关联。
        applicant: 申请人，外键关联用户。
        description: 工单描述。
        variables: 工单变量值（JSON 格式）。
        status: 工单状态。
        current_step: 当前审批步骤。
        created_at: 创建时间。
        updated_at: 更新时间。
        closed_at: 关闭时间。

    状态流转:
        draft -> pending -> approved/rejected -> closed

    示例:
        >>> template = TicketTemplate.objects.get(code='server_request')
        >>> Ticket.objects.create(
        ...     title='申请新服务器',
        ...     template=template,
        ...     applicant=user,
        ...     description='需要申请 2 台 8 核 16G 服务器'
        ... )
    """

    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('closed', '已关闭'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name='工单标题',
        help_text='工单的简要标题'
    )
    template = models.ForeignKey(
        TicketTemplate,
        on_delete=models.PROTECT,
        verbose_name='工单模板',
        help_text='工单所属的模板'
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_tickets',
        verbose_name='申请人',
        help_text='提交该工单的用户'
    )
    description = models.TextField(
        verbose_name='工单描述',
        help_text='工单的详细描述'
    )
    variables = models.TextField(
        null=True,
        blank=True,
        verbose_name='工单变量',
        help_text='JSON 格式的工单变量值'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态',
        help_text='工单状态'
    )
    current_step = models.IntegerField(
        default=0,
        verbose_name='当前步骤',
        help_text='当前审批步骤，从0开始'
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
        help_text='工单关闭时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'ticket'。
        按创建时间倒序排列。
        """
        db_table = 'ticket'
        verbose_name = '工单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        """返回工单描述."""
        return f"[{self.template.name}] {self.title}"


class ApprovalStep(models.Model):
    """审批步骤模型.

    定义工单的审批步骤顺序和审批人。

    属性:
        ticket: 所属工单，外键关联。
        step: 步骤序号，从0开始。
        approver: 审批人，外键关联用户。
        status: 步骤状态（pending/approved/rejected）。
        comment: 审批意见。
        created_at: 创建时间。
        completed_at: 完成时间。

    示例:
        >>> ticket = Ticket.objects.first()
        >>> ApprovalStep.objects.create(
        ...     ticket=ticket,
        ...     step=0,
        ...     approver=user,
        ...     status='pending'
        ... )
    """

    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='approval_steps',
        verbose_name='工单',
        help_text='所属工单'
    )
    step = models.IntegerField(
        verbose_name='步骤序号',
        help_text='审批步骤序号，从0开始'
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='approval_steps',
        verbose_name='审批人',
        help_text='该步骤的审批人'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态',
        help_text='审批状态'
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name='审批意见',
        help_text='审批人的意见'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='完成时间',
        help_text='审批完成时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'approval_step'。
        工单和步骤序号组合唯一，按步骤序号排序。
        """
        db_table = 'approval_step'
        verbose_name = '审批步骤'
        verbose_name_plural = verbose_name
        unique_together = ['ticket', 'step']
        ordering = ['step']

    def __str__(self) -> str:
        """返回步骤描述."""
        return f"{self.ticket.title} - 步骤{self.step}"


class ApprovalRecord(models.Model):
    """审批记录模型.

    记录每次审批操作的详细信息。

    属性:
        step: 所属步骤，外键关联。
        operator: 操作人，外键关联用户。
        action: 操作类型（approve/reject）。
        comment: 审批意见。
        created_at: 操作时间。

    示例:
        >>> step = ApprovalStep.objects.first()
        >>> ApprovalRecord.objects.create(
        ...     step=step,
        ...     operator=user,
        ...     action='approve',
        ...     comment='同意申请'
        ... )
    """

    ACTION_CHOICES = [
        ('approve', '批准'),
        ('reject', '拒绝'),
    ]

    step = models.ForeignKey(
        ApprovalStep,
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='审批步骤',
        help_text='所属审批步骤'
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='approval_records',
        verbose_name='操作人',
        help_text='执行审批操作的用户'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='操作',
        help_text='审批操作类型'
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name='审批意见',
        help_text='审批人的意见'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='操作时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'approval_record'。
        按操作时间正序排列。
        """
        db_table = 'approval_record'
        verbose_name = '审批记录'
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self) -> str:
        """返回记录描述."""
        return f"{self.operator.username} {self.get_action_display()} {self.step.ticket.title}"
