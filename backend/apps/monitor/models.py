"""Monitor 模块数据模型.

提供 Prometheus 监控集成相关的数据模型，包括 Prometheus 实例、告警规则、
告警记录和监控目标等。

数据模型:
    - PrometheusInstance: Prometheus 服务器实例配置
    - AlertRule: 告警规则配置
    - AlertRecord: 告警记录
    - MonitorTarget: 监控目标

典型使用场景:
    - 添加公司 Prometheus 服务器到平台
    - 配置监控告警规则
    - 接收和处理 Alertmanager 推送的告警
    - 管理被监控的主机和服务

告警流程:
    1. Prometheus 根据 AlertRule 评估告警条件
    2. 触发告警时发送给 Alertmanager
    3. Alertmanager 统一处理后 Webhook 推送到平台
    4. 平台创建 AlertRecord 记录告警
    5. 运维人员确认处理告警

示例:
    >>> from apps.monitor.models import PrometheusInstance, AlertRule
    >>> instance = PrometheusInstance.objects.create(
    ...     name='Prometheus主服务器',
    ...     url='http://prometheus.example.com'
    ... )
"""

import logging
from django.db import models

# 模块级日志记录器
logger = logging.getLogger(__name__)


class PrometheusInstance(models.Model):
    """Prometheus 实例模型.

    存储 Prometheus 服务器的连接信息，用于调用 Prometheus API。

    属性:
        name: 实例名称，最长 100 个字符。
        url: Prometheus 服务器地址，必须是有效的 URL 格式。
        api_token: API Token，可选，用于认证的 Bearer Token。
        is_active: 是否启用，禁用后不会使用该实例查询。

    示例:
        >>> PrometheusInstance.objects.create(
        ...     name='Prometheus主服务器',
        ...     url='http://prometheus.example.com',
        ...     api_token='your-token'
        ... )
    """

    name = models.CharField(
        max_length=100,
        verbose_name='实例名称',
        help_text='Prometheus 实例的显示名称'
    )
    url = models.URLField(
        verbose_name='Prometheus URL',
        help_text='Prometheus 服务器地址，如 http://prometheus.example.com'
    )
    api_token = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='API Token',
        help_text='可选的 API Token，用于认证'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='禁用后不会使用该实例进行查询'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'prometheus_instance'。
        """
        db_table = 'prometheus_instance'
        verbose_name = 'Prometheus 实例'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回实例的字符串表示.

        Returns:
            实例名称。
        """
        return self.name


class AlertRule(models.Model):
    """告警规则模型.

    定义告警条件，包括 PromQL 表达式、持续时间、严重级别等。

    属性:
        name: 规则名称，最长 100 个字符。
        prometheus: 所属 Prometheus 实例，外键关联。
        expr: PromQL 表达式，用于判断告警条件。
        duration: 持续时间（秒），条件满足多长时间后触发告警。
        severity: 严重级别，可选值：critical/warning/info。
        labels: 标签，JSON 格式，用于告警分组和路由。
        annotations: 描述信息，JSON 格式，用于告警展示和通知。
        enabled: 是否启用，禁用后不会评估该规则。
        created_at: 创建时间，自动设置。

    示例:
        >>> from apps.monitor.models import PrometheusInstance
        >>> instance = PrometheusInstance.objects.first()
        >>> AlertRule.objects.create(
        ...     name='CPU 使用率过高',
        ...     prometheus=instance,
        ...     expr='usage_cpu > 80',
        ...     duration=60,
        ...     severity='warning'
        ... )
    """

    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='规则名称',
        help_text='告警规则的显示名称'
    )
    prometheus = models.ForeignKey(
        PrometheusInstance,
        on_delete=models.CASCADE,
        verbose_name='所属实例',
        help_text='告警规则所属的 Prometheus 实例'
    )
    expr = models.TextField(
        verbose_name='PromQL 表达式',
        help_text='判断告警条件的 PromQL 表达式'
    )
    duration = models.IntegerField(
        default=60,
        verbose_name='持续时间(秒)',
        help_text='条件满足多少秒后触发告警'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='warning',
        verbose_name='级别',
        help_text='告警级别：critical-严重，warning-警告，info-信息'
    )
    labels = models.JSONField(
        default=dict,
        verbose_name='标签',
        help_text='告警标签，用于分组和路由'
    )
    annotations = models.JSONField(
        default=dict,
        verbose_name='描述',
        help_text='告警描述信息'
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='禁用后 Prometheus 不会评估该规则'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'alert_rule'。
        """
        db_table = 'alert_rule'
        verbose_name = '告警规则'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回规则的字符串表示.

        Returns:
            规则名称。
        """
        return self.name


class AlertRecord(models.Model):
    """告警记录模型.

    记录每次告警的详细信息，包括触发时间、状态、确认人等。

    属性:
        rule: 关联的告警规则，外键关联。
        status: 告警状态，可选值：firing/resolved/acknowledged。
        alert_name: 告警名称，来自 Prometheus 告警的 alertname 标签。
        labels: 告警标签，JSON 格式，包含告警的详细信息。
        annotations: 告警描述，JSON 格式。
        starts_at: 告警开始时间。
        ends_at: 告警结束时间（恢复时间），可选。
        acknowledged_by: 确认人，可选，记录处理该告警的用户。

    状态说明:
        - firing: 告警触发中
        - resolved: 告警已恢复
        - acknowledged: 告警已确认（运维人员已知悉）

    示例:
        >>> from apps.monitor.models import AlertRule
        >>> rule = AlertRule.objects.first()
        >>> AlertRecord.objects.create(
        ...     rule=rule,
        ...     status='firing',
        ...     alert_name='HighCPU',
        ...     labels={'instance': 'server1:9100'},
        ...     starts_at='2024-01-01T10:00:00Z'
        ... )
    """

    STATUS_CHOICES = [
        ('firing', '触发中'),
        ('resolved', '已恢复'),
        ('acknowledged', '已确认'),
    ]

    rule = models.ForeignKey(
        AlertRule,
        on_delete=models.CASCADE,
        verbose_name='关联规则',
        help_text='触发该记录的告警规则'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='firing',
        verbose_name='状态',
        help_text='告警状态：firing-触发中，resolved-已恢复，acknowledged-已确认'
    )
    alert_name = models.CharField(
        max_length=100,
        verbose_name='告警名称',
        help_text='告警名称，对应 Prometheus 告警的 alertname'
    )
    labels = models.JSONField(
        default=dict,
        verbose_name='标签',
        help_text='告警标签，JSON 格式'
    )
    annotations = models.JSONField(
        default=dict,
        verbose_name='描述',
        help_text='告警描述信息，JSON 格式'
    )
    starts_at = models.DateTimeField(
        verbose_name='开始时间',
        help_text='告警触发时间'
    )
    ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='结束时间',
        help_text='告警恢复时间'
    )
    acknowledged_by = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='确认人',
        help_text='确认该告警的用户'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'alert_record'，按开始时间倒序排列。
        """
        db_table = 'alert_record'
        verbose_name = '告警记录'
        verbose_name_plural = verbose_name
        ordering = ['-starts_at']

    def __str__(self) -> str:
        """返回告警记录的字符串表示.

        Returns:
            格式为"告警名 (状态)"的字符串。
        """
        return f"{self.alert_name} ({self.status})"


class MonitorTarget(models.Model):
    """监控目标模型.

    管理被监控的主机和服务，记录监控端点信息。

    属性:
        name: 目标名称，最长 100 个字符。
        target_type: 目标类型，如 host、service、container 等。
        address: 监控地址，如 http://host:9100/metrics。
        host: 关联的主机（可选），外键关联到 CMDB 主机。
        prometheus: 所属 Prometheus 实例，外键关联。
        labels: 标签，JSON 格式，用于服务发现和分组。
        is_active: 是否启用，禁用后不会采集该目标。

    示例:
        >>> from apps.monitor.models import PrometheusInstance
        >>> from apps.cmdb.models import Host
        >>> instance = PrometheusInstance.objects.first()
        >>> host = Host.objects.first()
        >>> MonitorTarget.objects.create(
        ...     name='服务器监控',
        ...     target_type='host',
        ...     address='http://192.168.1.1:9100/metrics',
        ...     host=host,
        ...     prometheus=instance
        ... )
    """

    name = models.CharField(
        max_length=100,
        verbose_name='目标名称',
        help_text='监控目标的显示名称'
    )
    target_type = models.CharField(
        max_length=50,
        verbose_name='目标类型',
        help_text='目标类型，如 host、service、container'
    )
    address = models.CharField(
        max_length=200,
        verbose_name='地址',
        help_text='监控端点地址，如 http://host:9100/metrics'
    )
    host = models.ForeignKey(
        'cmdb.Host',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='关联主机',
        help_text='关联的 CMDB 主机'
    )
    prometheus = models.ForeignKey(
        PrometheusInstance,
        on_delete=models.CASCADE,
        verbose_name='所属实例',
        help_text='监控目标所属的 Prometheus 实例'
    )
    labels = models.JSONField(
        default=dict,
        verbose_name='标签',
        help_text='监控目标标签，用于服务发现'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='禁用后 Prometheus 不会采集该目标'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'monitor_target'。
        """
        db_table = 'monitor_target'
        verbose_name = '监控目标'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回监控目标的字符串表示.

        Returns:
            目标名称。
        """
        return self.name
