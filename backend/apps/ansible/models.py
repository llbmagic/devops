"""Ansible 集成模块数据模型.

提供 Ansible 控制节点、剧本、执行记录的数据模型定义。
"""

import logging
from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


class AnsibleServer(models.Model):
    """Ansible 控制节点模型.

    存储 Ansible 控制节点的信息，用于执行 ansible-playbook 命令。

    属性:
        name: 服务器名称。
        host: 控制节点 IP 地址或主机名。
        ssh_port: SSH 端口，默认为 22。
        ssh_user: SSH 用户名。
        ssh_password: SSH 密码（建议使用密钥认证）。
        private_key_path: 私钥文件路径（可选）。
        description: 描述信息。
        is_active: 是否启用。
        created_at: 创建时间。

    示例:
        >>> AnsibleServer.objects.create(
        ...     name='Ansible Controller',
        ...     host='192.168.1.100',
        ...     ssh_user='root',
        ...     private_key_path='/root/.ssh/id_rsa'
        ... )
    """

    name = models.CharField(
        max_length=100,
        verbose_name='服务器名称',
        help_text='Ansible 控制节点的显示名称'
    )
    host = models.GenericIPAddressField(
        verbose_name='主机地址',
        help_text='Ansible 控制节点的 IP 地址或主机名'
    )
    ssh_port = models.IntegerField(
        default=22,
        verbose_name='SSH 端口',
        help_text='SSH 连接端口'
    )
    ssh_user = models.CharField(
        max_length=50,
        default='root',
        verbose_name='SSH 用户',
        help_text='SSH 连接用户名'
    )
    ssh_password = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='SSH 密码',
        help_text='SSH 密码（建议使用密钥认证）'
    )
    private_key_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='私钥路径',
        help_text='SSH 私钥文件路径'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='描述',
        help_text='控制节点的详细描述'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='禁用后不能通过该节点执行任务'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'ansible_server'。
        """
        db_table = 'ansible_server'
        verbose_name = 'Ansible 控制节点'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回服务器名称."""
        return self.name


class Playbook(models.Model):
    """剧本模型.

    存储 Ansible Playbook 的定义，包括名称、文件路径和参数。

    属性:
        name: 剧本名称。
        playbook_path: 剧本文件在控制节点上的路径。
        description: 剧本描述。
        variables: 预设变量（YAML 格式字符串）。
        created_by: 创建人。
        created_at: 创建时间。
        updated_at: 更新时间。

    示例:
        >>> Playbook.objects.create(
        ...     name='部署 Web 服务',
        ...     playbook_path='/opt/ansible/playbooks/deploy-web.yml',
        ...     variables='env: prod\nversion: latest'
        ... )
    """

    name = models.CharField(
        max_length=200,
        verbose_name='剧本名称',
        help_text='Playbook 的显示名称'
    )
    playbook_path = models.CharField(
        max_length=500,
        verbose_name='剧本路径',
        help_text='Playbook 文件在控制节点上的完整路径'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='描述',
        help_text='剧本的详细用途说明'
    )
    variables = models.TextField(
        null=True,
        blank=True,
        verbose_name='预设变量',
        help_text='YAML 格式的变量，如 env: prod'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='创建人',
        help_text='创建该剧本的用户'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'ansible_playbook'。
        """
        db_table = 'ansible_playbook'
        verbose_name = '剧本'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回剧本名称."""
        return self.name


class TaskRecord(models.Model):
    """任务执行记录模型.

    记录每次 ansible-playbook 执行的信息和结果。

    属性:
        playbook: 关联的剧本，外键关联。
        server: 使用的 Ansible 控制节点，外键关联。
        target_hosts: 目标主机列表字符串。
        variables: 执行时传入的变量。
        status: 执行状态（pending/running/success/failed）。
        executor: 执行人。
        output: 执行输出（截断到 10MB）。
        error: 错误信息。
        started_at: 开始时间。
        finished_at: 结束时间。

    示例:
        >>> server = AnsibleServer.objects.first()
        >>> playbook = Playbook.objects.first()
        >>> TaskRecord.objects.create(
        ...     playbook=playbook,
        ...     server=server,
        ...     target_hosts='web-01,web-02',
        ...     executor='admin',
        ...     status='success'
        ... )
    """

    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '执行中'),
        ('success', '成功'),
        ('failed', '失败'),
    ]

    playbook = models.ForeignKey(
        Playbook,
        on_delete=models.CASCADE,
        related_name='task_records',
        verbose_name='剧本',
        help_text='执行的剧本'
    )
    server = models.ForeignKey(
        AnsibleServer,
        on_delete=models.CASCADE,
        verbose_name='控制节点',
        help_text='使用的 Ansible 控制节点'
    )
    target_hosts = models.CharField(
        max_length=500,
        verbose_name='目标主机',
        help_text='目标主机列表，如 web-01,web-02 或 all'
    )
    variables = models.TextField(
        null=True,
        blank=True,
        verbose_name='执行变量',
        help_text='执行时传入的变量（JSON 或 YAML 格式）'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态',
        help_text='执行状态'
    )
    executor = models.CharField(
        max_length=100,
        verbose_name='执行人',
        help_text='执行任务的用户'
    )
    output = models.TextField(
        null=True,
        blank=True,
        verbose_name='执行输出',
        help_text='ansible-playbook 的标准输出和错误'
    )
    error = models.TextField(
        null=True,
        blank=True,
        verbose_name='错误信息',
        help_text='执行过程中的错误信息'
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='开始时间'
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='结束时间',
        help_text='任务完成时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'ansible_task_record'。
        按开始时间倒序排列。
        """
        db_table = 'ansible_task_record'
        verbose_name = '执行记录'
        verbose_name_plural = verbose_name
        ordering = ['-started_at']

    def __str__(self) -> str:
        """返回执行记录描述."""
        return f"{self.playbook.name} - {self.target_hosts} ({self.status})"
