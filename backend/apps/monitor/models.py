from django.db import models


class PrometheusInstance(models.Model):
    name = models.CharField(max_length=100, verbose_name='实例名称')
    url = models.URLField(verbose_name='Prometheus URL')
    api_token = models.CharField(max_length=200, null=True, blank=True, verbose_name='API Token')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        db_table = 'prometheus_instance'
        verbose_name = 'Prometheus 实例'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class AlertRule(models.Model):
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]
    name = models.CharField(max_length=100, verbose_name='规则名称')
    prometheus = models.ForeignKey(PrometheusInstance, on_delete=models.CASCADE, verbose_name='所属实例')
    expr = models.TextField(verbose_name='PromQL 表达式')
    duration = models.IntegerField(default=60, verbose_name='持续时间(秒)')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='warning', verbose_name='级别')
    labels = models.JSONField(default=dict, verbose_name='标签')
    annotations = models.JSONField(default=dict, verbose_name='描述')
    enabled = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alert_rule'
        verbose_name = '告警规则'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class AlertRecord(models.Model):
    STATUS_CHOICES = [
        ('firing', '触发中'),
        ('resolved', '已恢复'),
        ('acknowledged', '已确认'),
    ]
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, verbose_name='关联规则')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='firing', verbose_name='状态')
    alert_name = models.CharField(max_length=100, verbose_name='告警名称')
    labels = models.JSONField(default=dict, verbose_name='标签')
    annotations = models.JSONField(default=dict, verbose_name='描述')
    starts_at = models.DateTimeField(verbose_name='开始时间')
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    acknowledged_by = models.CharField(max_length=50, null=True, blank=True, verbose_name='确认人')

    class Meta:
        db_table = 'alert_record'
        verbose_name = '告警记录'
        verbose_name_plural = verbose_name
        ordering = ['-starts_at']

    def __str__(self):
        return f"{self.alert_name} ({self.status})"


class MonitorTarget(models.Model):
    """监控目标"""
    name = models.CharField(max_length=100, verbose_name='目标名称')
    target_type = models.CharField(max_length=50, verbose_name='目标类型')
    address = models.CharField(max_length=200, verbose_name='地址')
    host = models.ForeignKey('cmdb.Host', null=True, on_delete=models.SET_NULL, verbose_name='关联主机')
    prometheus = models.ForeignKey(PrometheusInstance, on_delete=models.CASCADE, verbose_name='所属实例')
    labels = models.JSONField(default=dict, verbose_name='标签')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        db_table = 'monitor_target'
        verbose_name = '监控目标'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name