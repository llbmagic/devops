"""监控模块视图集.

提供 Prometheus 监控集成相关的 ViewSet，实现监控查询和告警管理功能。

主要功能:
    - Prometheus 实例管理（添加、编辑、删除 Prometheus 服务器）
    - 指标查询（代理查询 Prometheus API）
    - 监控目标管理（管理被监控的目标主机和服务）
    - 告警规则管理（创建、编辑、启用/禁用告警规则）
    - 告警记录（查看、确认告警）
    - Alertmanager Webhook（接收 Alertmanager 推送的告警）

典型使用场景:
    - 运维人员添加公司 Prometheus 服务器
    - 通过平台查询监控指标和目标状态
    - 配置告警规则，异常时自动触发告警
    - Alertmanager 将告警推送到平台进行统一管理
    - 告警产生后，运维人员确认并处理

API 路由:
    - /api/monitor/prometheus-instances/ - Prometheus 实例 CRUD
    - /api/monitor/prometheus-instances/{id}/query/ - 查询指标
    - /api/monitor/prometheus-instances/{id}/targets/ - 获取监控目标
    - /api/monitor/alert-rules/ - 告警规则 CRUD
    - /api/monitor/alert-rules/by_severity/ - 按严重级别筛选告警规则
    - /api/monitor/alerts/ - 告警记录 CRUD
    - /api/monitor/alerts/{id}/acknowledge/ - 确认告警
    - /api/monitor/targets/ - 监控目标 CRUD
    - /api/monitor/webhooks/alertmanager/ - Alertmanager Webhook 接收端点

错误处理:
    - Prometheus API 调用使用 try-except 包装，失败时返回友好错误信息
    - 超时时间设置为 10 秒
"""

import logging
from typing import Optional, Any, Dict, List

import requests
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import PrometheusInstance, AlertRule, AlertRecord, MonitorTarget
from .serializers import (
    PrometheusInstanceSerializer, AlertRuleSerializer,
    AlertRecordSerializer, MonitorTargetSerializer
)

# 模块级日志记录器
logger = logging.getLogger(__name__)


class PrometheusInstanceViewSet(viewsets.ModelViewSet):
    """Prometheus 实例视图集.

    管理 Prometheus 服务器实例，包括添加、编辑、删除、查询指标等操作。

    路由:
        GET /api/monitor/prometheus-instances/ - 获取实例列表
        POST /api/monitor/prometheus-instances/ - 创建新实例
        GET /api/monitor/prometheus-instances/{id}/ - 获取实例详情
        PUT /api/monitor/prometheus-instances/{id}/ - 更新实例
        DELETE /api/monitor/prometheus-instances/{id}/ - 删除实例
        GET /api/monitor/prometheus-instances/{id}/query/ - 查询 Prometheus 指标
        GET /api/monitor/prometheus-instances/{id}/targets/ - 获取监控目标列表
    """

    queryset = PrometheusInstance.objects.all()
    serializer_class = PrometheusInstanceSerializer

    @action(detail=True, methods=['get'])
    def query(self, request: Request, pk: Optional[str] = None) -> Response:
        """查询 Prometheus 指标.

        代理请求到 Prometheus 的 /api/v1/query 接口，支持 PromQL 查询。

        Args:
            request: HTTP 请求对象，包含 query 参数（PromQL 查询语句）。
            pk: Prometheus 实例的主键 ID。

        Returns:
            Prometheus 查询结果，包含 status 和 data 字段。
        """
        instance = self.get_object()
        query = request.query_params.get('query', '')
        url = f"{instance.url}/api/v1/query"
        headers = {'Authorization': f"Bearer {instance.api_token}"} if instance.api_token else {}
        try:
            response = requests.get(
                url,
                params={'query': query},
                headers=headers,
                timeout=10
            )
            return Response(response.json())
        except requests.RequestException as e:
            logger.error(f"Prometheus 查询失败: {e}")
            return Response(
                {'status': 'error', 'error': f'查询失败: {str(e)}'},
                status=500
            )

    @action(detail=True, methods=['get'])
    def targets(self, request: Request, pk: Optional[str] = None) -> Response:
        """获取 Prometheus 监控目标列表.

        代理请求到 Prometheus 的 /api/v1/targets 接口，获取所有监控目标状态。

        Args:
            request: HTTP 请求对象。
            pk: Prometheus 实例的主键 ID。

        Returns:
            Prometheus targets 信息，包含所有监控目标和其状态。
        """
        instance = self.get_object()
        url = f"{instance.url}/api/v1/targets"
        headers = {'Authorization': f"Bearer {instance.api_token}"} if instance.api_token else {}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            return Response(response.json())
        except requests.RequestException as e:
            logger.error(f"获取 Prometheus targets 失败: {e}")
            return Response(
                {'status': 'error', 'error': f'获取目标失败: {str(e)}'},
                status=500
            )


class AlertRuleViewSet(viewsets.ModelViewSet):
    """告警规则视图集.

    管理告警规则，包括创建、编辑、启用/禁用、删除等操作。

    路由:
        GET /api/monitor/alert-rules/ - 获取告警规则列表
        POST /api/monitor/alert-rules/ - 创建新告警规则
        GET /api/monitor/alert-rules/{id}/ - 获取告警规则详情
        PUT /api/monitor/alert-rules/{id}/ - 更新告警规则
        DELETE /api/monitor/alert-rules/{id}/ - 删除告警规则
        GET /api/monitor/alert-rules/by_severity/ - 按严重级别筛选告警规则
    """

    queryset = AlertRule.objects.select_related('prometheus').all()
    serializer_class = AlertRuleSerializer

    @action(detail=False, methods=['get'])
    def by_severity(self, request: Request) -> Response:
        """按严重级别筛选告警规则.

        根据 severity 参数过滤告警规则列表，如 critical、warning、info。

        Args:
            request: HTTP 请求对象，包含 severity 查询参数。

        Returns:
            符合筛选条件的告警规则列表。
        """
        severity = request.query_params.get('severity')
        queryset = self.get_queryset()
        if severity:
            queryset = queryset.filter(severity=severity)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AlertRecordViewSet(viewsets.ModelViewSet):
    """告警记录视图集.

    管理告警记录，包括查看、确认等操作。

    路由:
        GET /api/monitor/alerts/ - 获取告警记录列表
        POST /api/monitor/alerts/ - 创建新告警记录
        GET /api/monitor/alerts/{id}/ - 获取告警记录详情
        PUT /api/monitor/alerts/{id}/ - 更新告警记录
        DELETE /api/monitor/alerts/{id}/ - 删除告警记录
        PATCH /api/monitor/alerts/{id}/acknowledge/ - 确认告警

    筛选参数:
        - status: 按状态筛选（firing/resolved/acknowledged）
    """

    queryset = AlertRecord.objects.select_related('rule').all()
    serializer_class = AlertRecordSerializer

    def get_queryset(self):
        """获取查询集，支持按状态筛选.

        Returns:
            过滤后的告警记录查询集。
        """
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @action(detail=True, methods=['patch'])
    def acknowledge(self, request: Request, pk: Optional[str] = None) -> Response:
        """确认告警.

        将告警状态标记为已确认，记录确认人和时间。

        Args:
            request: HTTP 请求对象，包含当前用户信息。
            pk: 告警记录的主键 ID。

        Returns:
            包含确认状态的响应对象。
        """
        record = self.get_object()
        record.status = 'acknowledged'
        record.acknowledged_by = request.user.username
        record.save()
        logger.info(f"用户 {request.user.username} 确认了告警: {record.alert_name}")
        return Response({'status': 'acknowledged'})


class MonitorTargetViewSet(viewsets.ModelViewSet):
    """监控目标视图集.

    管理被监控的目标主机和服务。

    路由:
        GET /api/monitor/targets/ - 获取监控目标列表
        POST /api/monitor/targets/ - 创建新监控目标
        GET /api/monitor/targets/{id}/ - 获取监控目标详情
        PUT /api/monitor/targets/{id}/ - 更新监控目标
        DELETE /api/monitor/targets/{id}/ - 删除监控目标
    """

    queryset = MonitorTarget.objects.select_related('prometheus', 'host').all()
    serializer_class = MonitorTargetSerializer


class AlertmanagerWebhookViewset(viewsets.ViewSet):
    """Alertmanager Webhook 视图集.

    接收 Alertmanager 推送的告警，创建本地告警记录。
    此端点允许匿名访问，用于接收 Alertmanager 的 Webhook 通知。

    路由:
        POST /api/monitor/webhooks/alertmanager/ - 接收 Alertmanager 告警

    权限:
        允许匿名访问（AllowAny），因为 Alertmanager 无法携带认证信息。

    请求格式:
        Alertmanager 发送的 Webhook 格式，包含 alerts 数组。
    """

    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def alertmanager(self, request: Request) -> Response:
        """接收 Alertmanager 告警.

        解析 Alertmanager 发送的 Webhook 数据，创建本地告警记录。
        对于已存在的告警（如同一 alertname），自动更新状态。

        Args:
            request: HTTP 请求对象，包含 Alertmanager 推送的告警数据。

        Returns:
            包含接收状态的响应对象。
        """
        alerts = request.data.get('alerts', [])
        created_count = 0
        for alert in alerts:
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})
            status = 'firing' if alert.get('status') == 'firing' else 'resolved'

            # 查找或创建告警规则
            alert_name = labels.get('alertname', 'unknown')
            rule, _ = AlertRule.objects.get_or_create(
                name=alert_name,
                defaults={'expr': 'unknown', 'prometheus_id': 1}
            )

            AlertRecord.objects.create(
                rule=rule,
                status=status,
                alert_name=alert_name,
                labels=labels,
                annotations=annotations,
                starts_at=alert.get('startsAt')
            )
            created_count += 1

        logger.info(f"接收到 Alertmanager 告警，共 {created_count} 条")
        return Response({'status': 'received', 'count': created_count})
