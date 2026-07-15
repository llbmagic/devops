"""Monitor 监控模块.

提供 Prometheus 监控集成相关的功能，包括实例管理、指标查询、告警规则管理、
告警记录和 Alertmanager Webhook 接收等。

公开子模块:
    - models: PrometheusInstance, AlertRule, AlertRecord, MonitorTarget
    - serializers: 各模型的序列化器
    - views: REST API 视图集
    - urls: 路由配置

典型使用场景:
    - 运维人员添加公司 Prometheus 服务器
    - 通过平台查询监控指标和目标状态
    - 配置告警规则，异常时自动触发告警
    - Alertmanager 将告警推送到平台进行统一管理
    - 告警产生后，运维人员确认并处理

示例:
    >>> from apps.monitor.models import PrometheusInstance, AlertRule
    >>> instance = PrometheusInstance.objects.create(name='Prometheus主服务器', url='http://prometheus.example.com')
"""

# 显式导出公开子模块（延迟导入，避免 AppRegistryNotReady）
__all__ = [
    'PrometheusInstance',
    'AlertRule',
    'AlertRecord',
    'MonitorTarget',
    'PrometheusInstanceSerializer',
    'AlertRuleSerializer',
    'AlertRecordSerializer',
    'MonitorTargetSerializer',
    'PrometheusInstanceViewSet',
    'AlertRuleViewSet',
    'AlertRecordViewSet',
    'MonitorTargetViewSet',
    'AlertmanagerWebhookViewset',
]
